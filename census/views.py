from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.template import Context, Template
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
import models
from .models import *
from django.contrib.auth.models import User, Group
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.forms import formset_factory
from django.db.models import Q
from django.contrib import admin
from itertools import chain
from django.core import serializers
from django.forms.models import model_to_dict
import json
from django.urls import reverse
from django.contrib import messages
#new import
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage

from datetime import datetime
import re

## UTILITY FUNCTIONS ##
# Eventually these should be moved into a separate util module.
def check_and_create_draft(selected_copy):
    assert selected_copy.drafts.count() < 2, "There should not be more than one Draft copies"
    if not selected_copy.drafts.exists():
        create_draft(selected_copy)

    draft_copy = selected_copy.drafts.get()
    return draft_copy

def lookup_draft(selected_copy):
    if not selected_copy.drafts.exists():
        print("no more more more draft") # problems found here
        return selected_copy
    else:
        print("draft")
        return selected_copy.drafts.get()

def search_sort_key(copy):
    return (int(copy.issue.start_date), title_sort_key(copy.issue.edition.title), strip_article(copy.location.name))

def strip_article(s):
    articles = ['a ', 'A ', 'an ', 'An ', 'the ', 'The ']
    for a in articles:
        if s.startswith(a):
            return s.replace(a, '', 1)
    else:
        return s

def title_sort_key(title_object):
    title = title_object.title
    if title and title[0].isdigit():
        title = title.split()
        return strip_article(' '.join(title[1:] + [title[0]]))
    else:
        return strip_article(title)

def issue_sort_key(i):
    ed_number = i.edition.Edition_number
    return int(ed_number) if ed_number.isdigit() else float('inf')

def copy_sort_key(c):
    return (strip_article(c.location.name), c.Shelfmark)

def convert_year_range(year):
    if '-' in year:
        start, end = [n.strip() for n in year.split('-', 1)]
        if len(start) == 4 and start.isdigit() and len(end) == 4 and end.isdigit():
            return int(start), int(end)
    elif len(year) == 4 and year.isdigit():
        return int(year), int(year)
    return False

def get_icon_path(id=None):
    if id is None:
        return 'census/images/title_icons/generic-title-icon.png'
    else:
    	return 'census/images/title_icons/{}.png'.format(id)

## VIEW FUNCTIONS ##

def search(request):
    template = loader.get_template('census/search-results.html')
    field = request.GET.get('field')
    value = request.GET.get('value')
    print(field)
    print(value)
    copy_list = CanonicalCopy.objects.all()

    if field == 'stc' or field is None and value:
	field = 'STC / Wing'
        result_list = copy_list.filter(issue__STC_Wing__icontains=value)
        print(result_list)
    elif field == 'year' and value:
        field = 'Year'
        year_range = convert_year_range(value)
        if year_range:
            start, end = year_range
            result_list = copy_list.filter(issue__start_date__lte=end, issue__end_date__gte=start)
        else:
            result_list = copy_list.filter(issue__year__icontains=value)
    elif field == 'location' and value:
        field = 'Location'
        result_list = copy_list.filter(location__name__icontains=value)
    elif field == 'bartlett' and value:
        field = 'Bartlett'
        result_list = copy_list.filter(Q(Bartlett1916=value) | Q(Bartlett1939=value))

    result_list = sorted(result_list, key=search_sort_key)

    context = {
        'icon_path': get_icon_path(),
        'value': value,
        'field': field,
        'result_list': result_list,
        'copy_count': len(result_list)
    }

    return HttpResponse(template.render(context, request))

def homepage(request):
    template = loader.get_template('census/frontpage.html')
    gridwidth = 5
    titlelist = sorted(Title.objects.all(), key=title_sort_key)
    titlerows = [titlelist[i: i + gridwidth]
                 for i in range(0, len(titlelist), gridwidth)]
    for row in titlerows:
        for t in row:
            t.icon_path = get_icon_path(t.id)
    context = {
        'frontpage': True,
        'titlelist': titlelist,
        'titlerows': titlerows,
    }
    return HttpResponse(template.render(context, request))

def about(request, viewname='about'):
    template = loader.get_template('census/about.html')
    copy_count = str(CanonicalCopy.objects.count())
    content = [(s.content.replace('{copy_count}', copy_count)
                         .replace('{current_date}', '{d:%d %B %Y}'.format(d=datetime.now())))
               for s in StaticPageText.objects.filter(viewname=viewname)]
    context =  {
        'content': content,
    }
    return HttpResponse(template.render(context, request))

def detail(request, id):
    selected_title=Title.objects.get(pk=id)
    if id == '5' or id == '6':
        editions = list(selected_title.edition_set.all())
        extra_ed = list(Title.objects.get(pk='39').edition_set.all())
        extra_ed[0].Edition_number = '3'
        editions.extend(extra_ed)
    else:
        editions = list(selected_title.edition_set.all())

    issues = [issue for ed in editions for issue in ed.issue_set.all()]
    issues.sort(key=issue_sort_key)
    copy_count = CanonicalCopy.objects.filter(issue__id__in=[i.id for i in issues]).count()
    template = loader.get_template('census/detail.html')
    context = {
        'icon_path': get_icon_path(id),
        'editions': editions,
        'issues': issues,
        'title': selected_title,
        'copy_count': copy_count,
    }
    return HttpResponse(template.render(context, request))

# showing all copies for an issue
def copy(request, id):
    selected_issue = Issue.objects.get(pk=id)
    all_copies = CanonicalCopy.objects.filter(issue__id=id).order_by('location__name', 'Shelfmark')
    all_copies = sorted(all_copies, key=copy_sort_key)
    template = loader.get_template('census/copy.html')
    context = {
        'all_copies': all_copies,
        'selected_issue': selected_issue,
        'icon_path': get_icon_path(selected_issue.edition.title.id),
        'title': selected_issue.edition.title
    }
    return HttpResponse(template.render(context, request))

def copy_data(request, copy_id):
    template = loader.get_template('census/copy_modal.html')

    selected_copy = CanonicalCopy.objects.get(pk=copy_id)
    selected_copy = lookup_draft(selected_copy)

    context={"copy": selected_copy}

    return HttpResponse(template.render(context, request))


# only want to show draft on the direct webpage
def admin_copy_data(request, id):
    template = loader.get_template('census/copy_modal.html')
    selected_copy = DraftCopy.objects.get(pk=id)
    context={"copy": selected_copy}
    return HttpResponse(template.render(context, request))


def login_user(request):
    template = loader.get_template('census/login.html')
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user_account = authenticate(username=username, password=password)
        if user_account is not None:
            login(request, user_account)
            next_url = request.POST.get('next',default=request.GET.get('next', 'login.html'))
            if request.GET.get('next') is None:
                if user_account.is_superuser:
                    next_url = "admin_start"
                else:
                    next_url = "librarian_start"

            return HttpResponseRedirect(next_url)
        else:
            return HttpResponse(template.render({'failed': True}, request))
    else:
        return HttpResponse(template.render({'next': request.GET.get('next', '')}, request))

def logout_user(request):
    template = loader.get_template('census/logout.html')
    logout(request)
    context = {}
    return HttpResponse(template.render(context,request))

#expected to be called when a new copy is submitted; displaying the copy info
def copy_info(request, copy_id):
    template = loader.get_template('census/copy_info.html')
    selected_copy = get_object_or_404(ChildCopy, pk=copy_id)
    selected_issue = selected_copy.issue
    selected_edition = selected_issue.edition
    context = {
        'selected_edition': selected_edition,
        'selected_copy': selected_copy,
    }
    return HttpResponse(template.render(context,request))

@login_required()
def submission(request):
    template = loader.get_template('census/submission.html')
    all_titles = Title.objects.all()
    copy_form = ChildCopyFormSubmit()

    if request.method=='POST':
        issue_id=request.POST.get('issue')
        if not issue_id or issue_id == 'Z':
            copy_form = ChildCopyFormSubmit()
            messages.error(request, 'Error: Please choose or add an issue.')
        else:
            selected_issue = Issue.objects.get(pk=issue_id)
            copy_form = ChildCopyFormSubmit(data=request.POST)
            if copy_form.is_valid():
                copy = copy_form.save(commit=False)
                copy.issue = selected_issue
                copy.created_by=request.user
                user_detail = UserDetail.objects.get(user=request.user)
                copy.location = user_detail.affiliation
                copy.librarian_validated = True
                copy.is_parent = False
                copy.false_positive = False
                copy.save()
                return HttpResponseRedirect(reverse('copy_info', args=(copy.id,)))
            else:
                copy_form = ChildCopyFormSubmit(data=request.POST)
                messages.error(request, 'Error: invalid copy information!')
    else:
        copy_form = ChildCopyFormSubmit()
    context = {
        'all_titles': all_titles,
        'copy_form': copy_form,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def edit_copy_submission(request, copy_id):
    template = loader.get_template('census/edit_submission.html')
    all_titles = Title.objects.all()
    copy_to_edit = CanonicalCopy.objects.get(pk=copy_id)
    old_issue = copy_to_edit.issue
    old_edition = old_issue.edition
    old_title = old_edition.title

    if request.method=='POST':
        issue_id=request.POST.get('issue')
        edition_id = request.POST.get('edition')
        title_id = request.POST.get('title')
        if not issue_id or issue_id == 'Z':
            copy_form = CopyForm(instance=copy_to_edit)
            messages.error(request, 'Error: Please choose or add an issue.')
        elif not edition_id or edition_id == 'Z':
            copy_form = CopyForm(instance=copy_to_edit)
            messages.error(request, 'Error: Please choose or add an edition.')
        elif not title_id or title_id == 'Z':
            copy_form = CopyForm(instance=copy_to_edit)
            messages.error(request, 'Error: Please choose or add a title.')

        else:
            selected_issue = Issue.objects.get(pk=issue_id)
            copy_form = CopyForm(request.POST, instance=copy_to_edit)

            if copy_form.is_valid():
                new_copy = copy_form.save()
                new_copy.issue = selected_issue
                new_copy.save(force_update=True)
                current_user = request.user
                current_userDetail = UserDetail.objects.get(user=current_user)
                current_userDetail.edited_copies.add(new_copy)
                return HttpResponseRedirect(reverse('copy_info', args=(new_copy.id,)))
            else:
                messages.error(request, 'Error: invalid copy information!')
                copy_form = CopyForm(data=request.POST)

    else:
        copy_form = CopyForm(instance=copy_to_edit)

    context = {
    'all_titles': all_titles,
    'copy_form': copy_form,
    'copy_id': copy_id,
    'old_title_id': old_title.id,
    'old_edition_set': old_title.edition_set.all(),
    'old_edition_id': old_edition.id,
    'old_issue_set': old_edition.issue_set.all(),
    'old_issue_id': old_issue.id,
    }
    return HttpResponse(template.render(context, request))

def copy_submission_success(request):
    template = loader.get_template('census/copysubmissionsuccess.html')
    context = {}
    return HttpResponse(template.render(context, request))

def cancel_copy_submission(request, copy_id):
    copy_to_delete = ChildCopy.objects.get(pk=copy_id)
    copy_to_delete.delete()
    return HttpResponseRedirect(reverse('submission'))

def json_editions(request, id):
    current_title = Title.objects.get(pk=id)
    editions = current_title.edition_set.all()
    data = []
    for edition in editions:
        data.append(model_to_dict(edition))
    return HttpResponse(json.dumps(data), content_type='application/json')

def json_issues(request, id):
    current_edition = Edition.objects.get(pk=id)
    issues = current_edition.issue_set.all()
    data = []
    for issue in issues:
        data.append(model_to_dict(issue))
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required()
def add_title(request):
    template = loader.get_template('census/add_title.html')
    if request.method == 'POST':
        title_form= TitleForm(data=request.POST)
        if title_form.is_valid():
            title = title_form.save(commit=True)
            myScript = '<script type="text/javascript">opener.dismissAddAnotherTitle(window, "%s", "%s");</script>' % (title.id, title.title)
            return HttpResponse(myScript)
        else:
            print(title_form.errors)
    else:
        title_form = TitleForm()

    context = {
       'title_form': title_form,
    }

    return HttpResponse(template.render(context, request))

@login_required()
def add_edition(request, title_id):
    template = loader.get_template('census/add_edition.html')
    selected_title =Title.objects.get(pk=title_id)
    if request.method=='POST':
        edition_form = EditionForm(data=request.POST)
        if edition_form.is_valid():
            edition = edition_form.save(commit=False)
            edition.title = selected_title
            edition.save()
            myScript = '<script type="text/javascript">opener.dismissAddAnotherEdition(window, "%s", "%s");</script>' % (edition.id, edition.Edition_number)
            return HttpResponse(myScript)
        else:
            print(edition_form.errors)
    else:
        edition_form = EditionForm()

    context = {
        'edition_form':edition_form,
        'title_id': title_id,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def add_copy(request, id):
    template = loader.get_template('census/copy_submission.html')
    selected_copy =  Issue.objects.get(pk=id)
    copy_submission_form = copySubMissionForm(request.POST or None)

    data = {'issue_id': id, 'location': 'affiliation_test', 'Shelfmark': 'required',
                           'Local_Notes': 'required', 'Prov_info': 'required'}
    if request.method == 'POST':
        copy_submission_form = copySubMissionForm(request.POST, initial=data)

        if copy_submission_form.is_valid():
            '''
            add draft
            linked to canonical_copy
            click to make prefilled word disappear
            move to the next page
            '''
            copy = copy_submission_form.save(commit=False)
            copy.issue = Issue.objects.get(pk=id)
            copy.location_verified = False
            copy.save()
            return HttpResponseRedirect(reverse('copy', args=(id,)))
    else:
        copy_submission_form = copySubMissionForm(initial=data)
        if not request.user.is_staff:
            # Add logic here to display the location
            del copy_submission_form.fields['location']
    context = {
       'form': copy_submission_form,
       'copy': selected_copy,
    }

    return HttpResponse(template.render(context, request))

@login_required()
def add_issue(request, edition_id):
    template = loader.get_template('census/add_issue.html')
    selected_edition =Edition.objects.get(pk=edition_id)

    if request.method=='POST':
        issue_form = IssueForm(data=request.POST)
        if issue_form.is_valid():
            issue = issue_form.save(commit=False)
            year_published = issue_form.cleaned_data['year']
            raw_nums = re.findall('\d+', year_published)
            issue.start_date = int(raw_nums[0])

            if len(raw_nums) == 1:
                issue.end_date = issue.start_date
            else:
                issue.end_date = raw_nums[1]

            issue.edition = selected_edition
            issue.save()
            myScript = '<script type="text/javascript">opener.dismissAddAnotherIssue(window, "%s", "%s");</script>' % (issue.id, issue.STC_Wing)
            return HttpResponse(myScript)
        else:
            print(issue_form.errors)
    else:
        issue_form = IssueForm()

    context = {
        'issue_form':issue_form,
        'edition_id': edition_id,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def display_user_profile(request):
    template = loader.get_template('census/user_profile.html')
    current_user = request.user
    context = {
        'user': current_user,
    }
    return HttpResponse(template.render(context, request))

@login_required
def librarian_start(request):
    template = loader.get_template('census/librarian/librarian_start_page.html')
    current_user = request.user
    cur_user_detail = UserDetail.objects.get(user=current_user)
    affiliation = cur_user_detail.affiliation

    copy_count = CanonicalCopy.objects.all().filter(location=affiliation,
                                                    location_verified=False).count()
    verified_count = CanonicalCopy.objects.all().filter(location=affiliation,
                                                        location_verified=True).count()

    context = {
        'affiliation': affiliation.name,
        'copy_count': copy_count,
        'verified_count': verified_count,
    }
    return HttpResponse(template.render(context, request))

def librarian_validate_sort_key(copy):
    return (title_sort_key(copy.issue.edition.title), int(copy.issue.start_date))

@login_required
def librarian_validate1(request):
    template = loader.get_template('census/librarian/librarian_validate1.html')
    current_user = request.user
    cur_user_detail = UserDetail.objects.get(user=current_user)
    affiliation = cur_user_detail.affiliation
    copy_list = CanonicalCopy.objects.filter(location=affiliation, location_verified=False)
    copy_list = sorted(copy_list, key=librarian_validate_sort_key)
    context = {
        'affiliation': affiliation.name,
        'copies': copy_list,
    }

    return HttpResponse(template.render(context, request))

@login_required
def librarian_validate2(request):
    template = loader.get_template('census/librarian/librarian_validate2.html')
    current_user = request.user
    cur_user_detail = UserDetail.objects.get(user=current_user)
    affiliation = cur_user_detail.affiliation
    child_copies = CanonicalCopy.objects.all().filter(location=affiliation,
                                        location_verified=True)
    child_copies = sorted(child_copies, key=librarian_validate_sort_key)
    context={
        'user_detail': cur_user_detail,
        'affiliation': affiliation.name,
        'child_copies': child_copies,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def update_draft_copy(request, id):
    template = loader.get_template('census/copy_submission.html')
    selected_copy = CanonicalCopy.objects.get(pk=id)
    copy = lookup_draft(selected_copy)
    data = {'issue_id': copy.issue.id, 'location': copy.location,
            'Shelfmark': copy.Shelfmark, 'Local_Notes': copy.Local_Notes,
            'Prov_info': copy.prov_info,
            }
    if request.method == 'POST':
        copy_form = createDraftForm(request.POST)

        if copy_form.is_valid():

            new_copy = copy_form.save(commit=False)
            new_copy.issue = copy.issue
            new_copy.location_verified = True
            new_copy.parent = selected_copy
            if isinstance(copy, DraftCopy):
                print("This is draftcopy")
                copy.delete()
            new_copy.save()
            return HttpResponseRedirect(reverse('librarian_validate2'))
    else:
        copy_form = createDraftForm(initial=data)
        context = {
        'form': copy_form,
        'copy': selected_copy,
        }
        return HttpResponse(template.render(context, request))

@login_required
def admin_start(request):
    template=loader.get_template('census/staff/admin_start_page.html')
    context={}
    return HttpResponse(template.render(context, request))


@login_required
def admin_edit_verify(request):
    template = template = loader.get_template('census/staff/admin_edit_verify.html')
    selected_copies = DraftCopy.objects.all()
    copies = [copy.parent for copy in selected_copies
    if isinstance(copy.parent, CanonicalCopy) and copy.parent.location_verified]

    paginator = Paginator(copies, 10)
    page = request.GET.get('page')
    try:
        copies_per_page = paginator.page(page)
    except PageNotAnInteger:
        copies_per_page = paginator.page(1)
    except EmptyPage:
        copies_per_page = paginator.page(paginator.num_pages)

    context={
        'copies': copies_per_page,
    }
    return HttpResponse(template.render(context, request))


@login_required
def admin_verify_single_edit_accept(request):
    try:
        copy_id = request.GET.get('copy_id')
    except IOError:
        print("something wrong with id, may be it does not exist at all?")
    selected_draft_copy = CanonicalCopy.objects.get(pk=copy_id).drafts.get()
    canonical_copy = selected_draft_copy.parent
    draft_to_canonical_update(selected_draft_copy)

    return HttpResponse('success')

@login_required
def admin_verify_single_edit_reject(request):
    try:
        copy_id = request.GET.get('copy_id')

    except IOError:
        print("something wrong with id, may be it does not exist at all?")
    selected_draft_copy = CanonicalCopy.objects.get(pk=copy_id).drafts.get()
    canonical_copy = selected_draft_copy.parent

    return HttpResponse('success')



@login_required
def admin_verify_location_verified(request): #fp -false_positive
    template = loader.get_template('census/staff/admin_verify.html')
    selected_copies = DraftCopy.objects.all()
    copies = [copy.parent for copy in selected_copies
    if isinstance(copy.parent, CanonicalCopy) and not copy.parent.location_verified]

    #copies = [copy for copy in selected_copies if copy.drafts.exists()]
    paginator = Paginator(copies, 10)
    page = request.GET.get('page')
    try:
        copies_per_page = paginator.page(page)
    except PageNotAnInteger:
        copies_per_page = paginator.page(1)
    except EmptyPage:
        copies_per_page = paginator.page(paginator.num_pages)

    context={
        'copies': copies_per_page,
    }
    return HttpResponse(template.render(context, request))

# This is for validate old copyx
@login_required()
def admin_verify_copy(request):
    try:
        copy_id = request.GET.get('copy_id')
    except IOError:
        print("something wrong with id, may be it does not exist at all?")
    selected_draft_copy = CanonicalCopy.objects.get(pk=copy_id).drafts.get()
    canonical_copy = selected_draft_copy.parent


    if not selected_draft_copy.location_verified:
        selected_draft_copy.delete()
        canonical_to_fp_move(canonical_copy)
    else:
        draft_to_canonical_update(selected_draft_copy)

    return HttpResponse('success')

@login_required()
def edit_profile(request):
    template=loader.get_template('census/edit_profile.html')
    current_user=request.user
    if request.method=='POST':
        profile_form = editProfileForm(request.POST, instance=current_user)
        if profile_form.is_valid():
            profile_form.save()
            return HttpResponseRedirect(reverse('profile'))
        else:
            messages.error(request, "The username you've inputted is already taken!")
    else:
        profile_form=editProfileForm(instance=current_user)

    context={
        'user': current_user,
        'profile_form': profile_form,
    }
    return HttpResponse(template.render(context, request))

#used by aja
@login_required
def create_draftcopy(request):

    try:
        copy_id = request.GET.get('copy_id')
    except IOError:
        print("something wrong with id, may be it does not exist at all?")


    selected_copy =  CanonicalCopy.objects.get(pk=copy_id)
    draft_copy = check_and_create_draft(selected_copy)
    draft_copy.location_verified = True
    draft_copy.save()

    return HttpResponse("success!")

@login_required
def location_incorrect(request):
    try:
        copy_id = request.GET.get('copy_id')
    except IOError:
        print("something wrong with id, may be it does not exist at all?")

    selected_copy =  CanonicalCopy.objects.get(pk=copy_id)
    draft_copy = check_and_create_draft(selected_copy)
    draft_copy.location_verified = False
    draft_copy.save()


    return HttpResponse("success!")

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user_detail = UserDetail.objects.get(user=user)
            user_detail.affiliation = form.cleaned_data['affiliation']
            user_detail.save()
            current_site = get_current_site(request)
            email_validation = False
            if email_validation:
                message = render_to_string('signup/acc_active_email.html', {
                    'user':user,
                    'domain':current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                mail_subject = 'Activate your librarian account.'
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
                return HttpResponse('Please confirm your email address to complete the registration')
            else:
		messages.success(request, 'Your account request has been received. A site administrator may contact you for more information.')
                return HttpResponseRedirect(reverse('signup'))

    else:
        form = SignupForm()

    return render(request, 'signup/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user_detail = UserDetail.objects.get(user=user)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        user_detail = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        user_detail.save()
        login(request, user)

        return HttpResponseRedirect('/profile')
    else:
        return HttpResponse('Activation link is invalid!')

def contact(request):
    template=loader.get_template('census/contact-form.html')

    if request.method=='POST':
        form=ContactUs(request.POST)
        if form.is_valid() and form.data['guardian'] == "":
            form.save()
            return HttpResponseRedirect(reverse('contact_success'))
        elif form.is_valid() and form.data['guardian'] != "":
            return HttpResponseRedirect(reverse('contact_success'))
        else:
            messages.error(request, "This form is invalid")
    else:
        form=ContactUs()

    context={'form': form}
    return HttpResponse(template.render(context, request))

def display_contact_success(request):
    template = loader.get_template('census/contact-form-success.html')
    current_user = request.user
    context = {
        'user': current_user,
    }
    return HttpResponse(template.render(context, request))
