from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.template import Context, Template
from django.shortcuts import render, get_object_or_404
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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re

def search(request):
    template = loader.get_template('census/search-results.html')
    field = request.GET.get('field')
    value = request.GET.get('value')
    print(field)
    print(value)
    copy_list = Copy.objects.all()

    if field == 'stc' and value:
        result_list = copy_list.filter(issue__STC_Wing__icontains=value, is_parent=True)
        print(result_list)

    elif field == 'year' and value:
        result_list = copy_list.filter(issue__year=value, is_parent=True)

    elif field == 'location' and value:
        result_list = copy_list.filter(Owner__icontains=value, is_parent=True)

    else:
        result_list = []

    context = {
        'value': value,
        'field': field,
        'result_list': result_list
    }

    return HttpResponse(template.render(context, request))
    # template = loader.get_template('census/results.html')
    # query1 = request.GET.get('a')
    # query2 = request.GET.get('b')
    # query3 = request.GET.get('c')
    # query4 = request.GET.get('d')
    #
    # category1 = request.GET.get('j')
    # category2 = request.GET.get('k')
    # category3 = request.GET.get('l')
    # category4 = request.GET.get('z')
    #
    # copy_list = Copy.objects.all().filter(
    #     is_parent=True, is_history=False
    # ).exclude(
    #     false_positive=True
    # )
    #
    # result_list = None
    # if query1 and not query2 and not query3 and not query4:
    #     results_list = copy_list.filter(Q(**{category1: query1}))
    #     result_list = list(chain(results_list))
    #
    # if query1 and query2 and not query3 and not query4:
    #     results_list = copy_list.filter(
    #         Q(**{category1: query1}) & Q(**{category2: query2})
    #     )
    #     result_list = list(chain(results_list))
    #
    # if query1 and query2 and query3 and not query4:
    #     results_list = copy_list.filter(
    #         Q(**{category1: query1}) &
    #         Q(**{category2: query2}) &
    #         Q(**{category3: query3})
    #     )
    #     result_list = list(chain(results_list))
    #
    # if query1 and query2 and query3 and query4:
    #     results_list = copy_list.filter(
    #         Q(**{category1: query1}) &
    #         Q(**{category2: query2}) &
    #         Q(**{category4: query4})
    #     )
    #     result_list = list(chain(results_list))
    #
    # if not query1 and not query2 and not query3 and not query4:
    #     results_list = copy_list.filter(
    #         Q(**{category1: query1}) &
    #         Q(**{category2: query2}) &
    #         Q(**{category4: query4})
    #     )
    #     result_list = list(chain(results_list))
    #
    # paginator = Paginator(result_list, 10)
    # page = request.GET.get('page')
    # try:
    #     results = paginator.page(page)
    # except PageNotAnInteger:
    #     results = paginator.page(1)
    # except EmptyPage:
    #     results = paginator.page(paginator.num_pages)
    #
    # context = {
    #         'result_list': results,
    #         'query1': query1,
    #         'query2': query2,
    #         'query3': query3,
    #         'query4': query4,
    #         'category1': category1,
    #         'category2': category2,
    #         'category3': category3,
    #         'category4': category4,
    #     }
    # return HttpResponse(template.render(context, request))

def title_sort_key(title_object):
    title = title_object.title
    if title and title[0].isdigit():
        title = title.split()
        return ' '.join(title[1:] + [title[0]])
    else:
        return title

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
    context =  { 
        'content': StaticPageText.objects.filter(viewname=viewname)
    }
    return HttpResponse(template.render(context, request))

# showing all titles in the database
def index(request):
    all_titles = Title.objects.all().order_by('title')
    template = loader.get_template('census/index.html')
    queryset_list = Title.objects.all()
    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(Q(title__icontains=query))
        paginator = Paginator(queryset_list, 10)  # Show 10 titles per page
        page = request.GET.get('page')
        try:
            queryset_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            queryset_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            queryset_list = paginator.page(paginator.num_pages)
        context = {
            'query': query,
            'object_list': queryset_list,
        }

    else:
        paginator = Paginator(all_titles, 10)  # Show 10 titles per page
        page = request.GET.get('page')
        try:
            titles = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            titles = paginator.page(1)
        except EmptyPage:
            #If page is out of range, deliver last page of results.
            titles = paginator.page(paginator.num_pages)

        context = {
            'object_list': queryset_list,
            'titles': titles,
        }
    return HttpResponse(template.render(context, request))

def issue_sort_key(i):
    ed_number = i.edition.Edition_number
    return int(ed_number) if ed_number.isdigit() else float('inf')

def detail(request, id):
    selected_title=Title.objects.get(pk=id)
    editions = list(selected_title.edition_set.all())
    issues = [issue for ed in editions for issue in ed.issue_set.all()]
    issues.sort(key=issue_sort_key)
    copy_count = sum(i.copy_set.filter(is_parent=True).count() for i in issues)
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
    all_copies = selected_issue.copy_set.filter(is_parent=True).order_by('Owner', 'Shelfmark')
    template = loader.get_template('census/copy.html')
    context = {
        'all_copies': all_copies,
        'selected_issue': selected_issue,
        'icon_path': get_icon_path(selected_issue.edition.title.id),
        'title': selected_issue.edition.title
    }
    return HttpResponse(template.render(context, request))


# showing all copies in the database
def copylist(request):
    all_copies = Copy.objects.all().filter(
        is_parent=True, is_history=False
    ).exclude(
        false_positive=True
    ).order_by(
        'issue__start_date', 'issue__edition__title__title'
    )
    template = loader.get_template('census/copylist.html')
    queryset_list = Copy.objects.all().filter(
        is_parent=True, is_history=False
    ).exclude(
        false_positive=True
    ).order_by('issue__start_date', 'issue__edition__title__title')
    query = request.GET.get("q")

    if query:
        if not query.isdigit():
            queryset_list = queryset_list.filter(
                Q(issue__edition__title__title__icontains=query) |
                Q(Owner__icontains=query) |
                Q(issue__ESTC=query) |
                Q(issue__STC_Wing=query)
            )
        elif query.isdigit():
            queryset_list = queryset_list.filter(
                Q(issue=query) |
                Q(issue__edition__Edition_number=query) |
                Q(issue__start_date=query) |
                Q(issue__end_date=query) | Q(issue__STC_Wing=query)
            )

        paginator = Paginator(queryset_list, 10)
        page = request.GET.get('page')
        try:
            queryset_list = paginator.page(page)
        except PageNotAnInteger:
            queryset_list = paginator.page(1)
        except EmptyPage:
            queryset_list = paginator.page(paginator.num_pages)
        context = {
            'query': query,
            'object_list': queryset_list,
        }

    else:
        paginator = Paginator(all_copies, 10)
        page = request.GET.get('page')
        try:
            copies = paginator.page(page)
        except PageNotAnInteger:
            copies = paginator.page(1)
        except EmptyPage:
            copies = paginator.page(paginator.num_pages)

        context = {
            'object_list': queryset_list,
            'copies': copies,
        }
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
    template=loader.get_template('census/copy_info.html')
    selected_copy=get_object_or_404(ChildCopy, pk=copy_id)
    selected_issue=selected_copy.issue
    selected_edition=selected_issue.edition
    context={
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
            copy_form=ChildCopyFormSubmit()
            messages.error(request, 'Error: Please choose or add an issue.')
        else:
            selected_issue=Issue.objects.get(pk=issue_id)
            copy_form=ChildCopyFormSubmit(data=request.POST)
            if copy_form.is_valid():
                copy=copy_form.save(commit=False)
                copy.issue=selected_issue
                copy.created_by=request.user
                user_detail=UserDetail.objects.get(user=request.user)
                copy.Owner=user_detail.affiliation
                copy.librarian_validated=True
                copy.is_parent=False
                copy.false_positive=False
                copy.save()
                return HttpResponseRedirect(reverse('copy_info', args=(copy.id,)))
            else:
                copy_form=ChildCopyFormSubmit(data=request.POST)
                messages.error(request, 'Error: invalid copy information!')
    else:
        copy_form=ChildCopyFormSubmit()
    context = {
        'all_titles': all_titles,
        'copy_form': copy_form,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def edit_copy_submission(request, copy_id):
    template = loader.get_template('census/edit_submission.html')
    all_titles = Title.objects.all()
    copy_to_edit=ChildCopy.objects.get(pk=copy_id)
    old_issue=copy_to_edit.issue
    old_edition=old_issue.edition
    old_title=old_edition.title

    if request.method=='POST':
        issue_id=request.POST.get('issue')
        edition_id=request.POST.get('edition')
        title_id=request.POST.get('title')
        if not issue_id or issue_id == 'Z':
            copy_form=CopyForm(instance=copy_to_edit)
            messages.error(request, 'Error: Please choose or add an issue.')
        elif not edition_id or edition_id == 'Z':
            copy_form=CopyForm(instance=copy_to_edit)
            messages.error(request, 'Error: Please choose or add an edition.')
        elif not title_id or title_id == 'Z':
            copy_form=CopyForm(instance=copy_to_edit)
            messages.error(request, 'Error: Please choose or add a title.')

        else:
            selected_issue=Issue.objects.get(pk=issue_id)
            copy_form=CopyForm(request.POST, instance=copy_to_edit)

            if copy_form.is_valid():
                new_copy=copy_form.save()
                new_copy.issue = selected_issue
                new_copy.save(force_update=True)
                current_user = request.user
                current_userDetail=UserDetail.objects.get(user=current_user)
                current_userDetail.edited_copies.add(new_copy)
                return HttpResponseRedirect(reverse('copy_info', args=(new_copy.id,)))
            else:
                messages.error(request, 'Error: invalid copy information!')
                copy_form=CopyForm(data=request.POST)

    else:
        copy_form=CopyForm(instance=copy_to_edit)

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
    template=loader.get_template('census/copysubmissionsuccess.html')
    context={}
    return HttpResponse(template.render(context, request))

def cancel_copy_submission(request, copy_id):
    copy_to_delete=ChildCopy.objects.get(pk=copy_id)
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
    template=loader.get_template('census/add_title.html')
    if request.method == 'POST':
        title_form= TitleForm(data=request.POST)
        if title_form.is_valid():
            title = title_form.save(commit=True)
            myScript = '<script type="text/javascript">opener.dismissAddAnotherTitle(window, "%s", "%s");</script>' % (title.id, title.title)
            return HttpResponse(myScript)
        else:
            print(title_form.errors)
    else:
        title_form=TitleForm()

    context = {
       'title_form': title_form,
    }

    return HttpResponse(template.render(context, request))

@login_required()
def add_edition(request, title_id):
    template=loader.get_template('census/add_edition.html')
    selected_title =Title.objects.get(pk=title_id)
    if request.method=='POST':
        edition_form=EditionForm(data=request.POST)
        if edition_form.is_valid():
            edition=edition_form.save(commit=False)
            edition.title=selected_title
            edition.save()
            myScript = '<script type="text/javascript">opener.dismissAddAnotherEdition(window, "%s", "%s");</script>' % (edition.id, edition.Edition_number)
            return HttpResponse(myScript)
        else:
            print(edition_form.errors)
    else:
        edition_form=EditionForm()

    context={
        'edition_form':edition_form,
        'title_id': title_id,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def add_issue(request, edition_id):
    template=loader.get_template('census/add_issue.html')
    selected_edition =Edition.objects.get(pk=edition_id)

    if request.method=='POST':
        issue_form=IssueForm(data=request.POST)
        if issue_form.is_valid():
            issue=issue_form.save(commit=False)
            year_published=issue_form.cleaned_data['year']
            raw_nums = re.findall('\d+', year_published)
            issue.start_date = int(raw_nums[0])

            if len(raw_nums) == 1:
                issue.end_date = issue.start_date
            else:
                issue.end_date = raw_nums[1]

            issue.edition=selected_edition
            issue.save()
            myScript = '<script type="text/javascript">opener.dismissAddAnotherIssue(window, "%s", "%s");</script>' % (issue.id, issue.STC_Wing)
            return HttpResponse(myScript)
        else:
            print(issue_form.errors)
    else:
        issue_form=IssueForm()

    context={
        'issue_form':issue_form,
        'edition_id': edition_id,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def display_user_profile(request):
    template=loader.get_template('census/user_profile.html')
    current_user=request.user
    context={
        'user': current_user,
    }
    return HttpResponse(template.render(context, request))

@login_required
def librarian_start(request):
    template=loader.get_template('census/librarian_start_page.html')
    current_user=request.user
    cur_user_detail=UserDetail.objects.get(user=current_user)
    affiliation=cur_user_detail.affiliation
    copy_count=Copy.objects.all().filter(Owner=affiliation, false_positive_draft=None,
                                         librarian_validated=False, is_parent=True, is_history=False).count()
    verified_count=Copy.objects.all().filter(Owner=affiliation, librarian_validated=True,
                                             is_parent=True, is_history=False).count()
    context={
        'affiliation': affiliation,
        'copy_count': copy_count,
        'verified_count': verified_count,
    }
    return HttpResponse(template.render(context, request))

@login_required
def librarian_validate1(request):
    template=loader.get_template('census/librarian_validate1.html')
    current_user=request.user
    cur_user_detail=UserDetail.objects.get(user=current_user)
    affiliation=cur_user_detail.affiliation
    copy_list=Copy.objects.all().filter(Owner=affiliation, from_estc=True, librarian_validated=False, \
              is_parent=True, is_history=False, false_positive_draft=None, false_positive=None)

    paginator = Paginator(copy_list, 10)
    page = request.GET.get('page')
    try:
        copies = paginator.page(page)
    except PageNotAnInteger:
        copies = paginator.page(1)
    except EmptyPage:
        copies = paginator.page(paginator.num_pages)

    context={
        'affiliation': affiliation,
        'copies': copies,
    }
    return HttpResponse(template.render(context, request))

@login_required
def validate_hold(request, id):
    selected_copy = Copy.objects.get(pk=id)

    ChildCopy.objects.create(Owner=selected_copy.Owner, issue=selected_copy.issue, \
    thumbnail_URL=selected_copy.thumbnail_URL, NSC=selected_copy.NSC, Shelfmark=selected_copy.Shelfmark,\
    Height=selected_copy.Height, Width=selected_copy.Width, Marginalia=selected_copy.Marginalia, \
    Condition=selected_copy.Condition, Binding=selected_copy.Binding, Binder=selected_copy.Binder, \
    Bookplate=selected_copy.Bookplate, Bookplate_Location=selected_copy.Bookplate_Location, Bartlett1939=selected_copy.Bartlett1939,\
    Bartlett1939_Notes=selected_copy.Bartlett1939_Notes, Bartlett1916=selected_copy.Bartlett1916, Bartlett1916_Notes=selected_copy.Bartlett1916_Notes,\
    Lee_Notes=selected_copy.Lee_Notes, Local_Notes=selected_copy.Local_Notes, created_by=selected_copy.created_by,\
    prov_info=selected_copy.prov_info, from_estc=selected_copy.from_estc,\
    librarian_validated=False, admin_validated=False, is_parent=False, is_history=False, held_by_library=True, parent=selected_copy)

    data='success'
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def validate_not_hold(request, id):
    selected_copy = Copy.objects.get(pk=id)

    ChildCopy.objects.create(Owner=selected_copy.Owner, issue=selected_copy.issue, \
    thumbnail_URL=selected_copy.thumbnail_URL, NSC=selected_copy.NSC, Shelfmark=selected_copy.Shelfmark,\
    Height=selected_copy.Height, Width=selected_copy.Width, Marginalia=selected_copy.Marginalia, \
    Condition=selected_copy.Condition, Binding=selected_copy.Binding, Binder=selected_copy.Binder, \
    Bookplate=selected_copy.Bookplate, Bookplate_Location=selected_copy.Bookplate_Location, Bartlett1939=selected_copy.Bartlett1939,\
    Bartlett1939_Notes=selected_copy.Bartlett1939_Notes, Bartlett1916=selected_copy.Bartlett1916, Bartlett1916_Notes=selected_copy.Bartlett1916_Notes,\
    Lee_Notes=selected_copy.Lee_Notes, Local_Notes=selected_copy.Local_Notes, created_by=selected_copy.created_by,\
    prov_info=selected_copy.prov_info, from_estc=selected_copy.from_estc,\
    librarian_validated=False, admin_validated=False, is_parent=False, is_history=False, held_by_library=False, parent=selected_copy)

    data='success'
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def change_hold_status(request, id):
    selected_copy=ChildCopy.objects.get(pk=id)
    if selected_copy.held_by_library:
        selected_copy.held_by_library = False
    else:
        selected_copy.held_by_library = True
    selected_copy.save()
    data='success'
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def change_false_positive_draft(request, id):
    selected_copy=ChildCopy.objects.get(pk=id)
    parent=selected_copy.parent
    if selected_copy.held_by_library:
        selected_copy.false_positive_draft = False
        parent.false_positive_draft=False
    else:
        selected_copy.false_positive_draft = True
        parent.false_positive_draft=True

    selected_copy.save()
    parent.save()
    data='success'
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def librarian_validate2(request):
    template=loader.get_template('census/librarian_validate2.html')
    current_user=request.user
    cur_user_detail=UserDetail.objects.get(user=current_user)
    affiliation=cur_user_detail.affiliation
    child_copies=ChildCopy.objects.all().filter(Owner=affiliation, librarian_validated=False, false_positive=False)

    context={
        'user_detail': cur_user_detail,
        'affiliation': affiliation,
        'child_copies': child_copies,
    }
    return HttpResponse(template.render(context, request))

def librarian_confirm(request, id):
    #Librarian confirms all infor is correct; the childcopy's librarian_validated will be marked true; so is its parent
    selected_copy = ChildCopy.objects.get(pk=id)
    selected_copy.librarian_validated = True
    selected_copy.parent.librarian_validated=True
    selected_copy.save()
    selected_copy.parent.save()
    data='success'
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def admin_start(request):
    template=loader.get_template('census/admin_start_page.html')
    context={}
    return HttpResponse(template.render(context, request))

@login_required
def admin_verify_fp(request): #fp -false_positive
    template=loader.get_template('census/admin_verify_fp.html')
    selected_copies=ChildCopy.objects.all().filter(false_positive=None).exclude(false_positive_draft=None)

    paginator = Paginator(selected_copies, 10)
    page = request.GET.get('page')
    try:
        copies = paginator.page(page)
    except PageNotAnInteger:
        copies = paginator.page(1)
    except EmptyPage:
        copies = paginator.page(paginator.num_pages)

    context={
        'copies': copies,
    }
    return HttpResponse(template.render(context, request))

@login_required
def admin_verify_copy_fp(request, copy_id):
    """admin verifies the false_positive attribute of a copy"""
    selected_copy=ChildCopy.objects.get(pk=copy_id)
    copy_parent = selected_copy.parent
    if selected_copy.false_positive_draft:
        #create a copyHistory object and copy all copy_parent info to that object
        copyHistory=CopyHistory.objects.create(Owner=copy_parent.Owner, issue=copy_parent.issue, \
        thumbnail_URL=copy_parent.thumbnail_URL, NSC=copy_parent.NSC, Shelfmark=copy_parent.Shelfmark,\
        Height=copy_parent.Height, Width=copy_parent.Width, Marginalia=copy_parent.Marginalia, \
        Condition=copy_parent.Condition, Binding=copy_parent.Binding, Binder=copy_parent.Binder, \
        Bookplate=copy_parent.Bookplate, Bookplate_Location=copy_parent.Bookplate_Location, Bartlett1939=copy_parent.Bartlett1939,\
        Bartlett1939_Notes=copy_parent.Bartlett1939_Notes, Bartlett1916=copy_parent.Bartlett1916, Bartlett1916_Notes=copy_parent.Bartlett1916_Notes,\
        Lee_Notes=copy_parent.Lee_Notes, Local_Notes=copy_parent.Local_Notes, created_by=copy_parent.created_by,\
        prov_info=copy_parent.prov_info, librarian_validated=False, \
        admin_validated=True, is_history=True, is_parent=False, from_estc=copy_parent.from_estc, false_positive=True, \
        stored_copy=None)

        copy_parent.delete()
        selected_copy.delete()
    else:
        copy_parent.false_positive=False
        selected_copy.false_positive=False
        selected_copy.save()
        copy_parent.save()

    data='success'
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def admin_verify(request):
    template=loader.get_template('census/admin_verify.html')
    all_copies=ChildCopy.objects.all()
    copy_list=[copy for copy in all_copies if copy.librarian_validated and not copy.admin_validated]

    paginator = Paginator(copy_list, 10)
    page = request.GET.get('page')
    try:
        copies = paginator.page(page)
    except PageNotAnInteger:
        copies = paginator.page(1)
    except EmptyPage:
        copies = paginator.page(paginator.num_pages)

    context={
        'copies': copies,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def admin_verify_copy(request, id):
    selected_copy = ChildCopy.objects.get(pk=id)
    data=[]
    if selected_copy.parent:  #if this child copy has parent, i.e. not directly submitted
        copy_parent=selected_copy.parent

        #create a copyHistory object and copy all copy_parent info to that object
        copyHistory=CopyHistory.objects.create(Owner=copy_parent.Owner, issue=copy_parent.issue, \
        thumbnail_URL=copy_parent.thumbnail_URL, NSC=copy_parent.NSC, Shelfmark=copy_parent.Shelfmark,\
        Height=copy_parent.Height, Width=copy_parent.Width, Marginalia=copy_parent.Marginalia, \
        Condition=copy_parent.Condition, Binding=copy_parent.Binding, Binder=copy_parent.Binder, \
        Bookplate=copy_parent.Bookplate, Bookplate_Location=copy_parent.Bookplate_Location, Bartlett1939=copy_parent.Bartlett1939,\
        Bartlett1939_Notes=copy_parent.Bartlett1939_Notes, Bartlett1916=copy_parent.Bartlett1916, Bartlett1916_Notes=copy_parent.Bartlett1916_Notes,\
        Lee_Notes=copy_parent.Lee_Notes, Local_Notes=copy_parent.Local_Notes, created_by=copy_parent.created_by,\
        prov_info=copy_parent.prov_info, librarian_validated=copy_parent.librarian_validated, \
        admin_validated=copy_parent.admin_validated, is_history=True, is_parent=False, from_estc=copy_parent.from_estc, \
        false_positive=copy_parent.false_positive, stored_copy=copy_parent)

        #update parent copy info:
        copy_parent.Owner=selected_copy.Owner
        copy_parent.issue=selected_copy.issue
        copy_parent.thumbnail_URL=selected_copy.thumbnail_URL
        copy_parent.NSC=selected_copy.NSC
        copy_parent.Shelfmark=selected_copy.Shelfmark
        copy_parent.Height=selected_copy.Height
        copy_parent.Width=selected_copy.Width
        copy_parent.Marginalia=selected_copy.Marginalia
        copy_parent.Condition=selected_copy.Condition
        copy_parent.Binding=selected_copy.Binding
        copy_parent.Binder=selected_copy.Binder
        copy_parent.Bookplate=selected_copy.Bookplate
        copy_parent.Bookplate_Location=selected_copy.Bookplate_Location
        copy_parent.Bartlett1939=selected_copy.Bartlett1939
        copy_parent.Bartlett1939_Notes=selected_copy.Bartlett1939_Notes
        copy_parent.Bartlett1916=selected_copy.Bartlett1916
        copy_parent.Bartlett1916_Notes=selected_copy.Bartlett1916_Notes
        copy_parent.Lee_Notes=selected_copy.Lee_Notes
        copy_parent.Local_Notes=selected_copy.Local_Notes
        copy_parent.created_by=selected_copy.created_by
        copy_parent.prov_info=selected_copy.prov_info
        copy_parent.false_positive=False
        copy_parent.librarian_validated=True
        copy_parent.admin_validated=True

        copy_parent.save()

        #delete the child copy
        selected_copy.delete()

        data.append(model_to_dict(copy_parent))

    else:
        #create a new parent copy
        new_copy=Copy.objects.create(Owner=selected_copy.Owner, issue=selected_copy.issue, \
        thumbnail_URL=selected_copy.thumbnail_URL, NSC=selected_copy.NSC, Shelfmark=selected_copy.Shelfmark,\
        Height=selected_copy.Height, Width=selected_copy.Width, Marginalia=selected_copy.Marginalia, \
        Condition=selected_copy.Condition, Binding=selected_copy.Binding, Binder=selected_copy.Binder, \
        Bookplate=selected_copy.Bookplate, Bookplate_Location=selected_copy.Bookplate_Location, Bartlett1939=selected_copy.Bartlett1939,\
        Bartlett1939_Notes=selected_copy.Bartlett1939_Notes, Bartlett1916=selected_copy.Bartlett1916, Bartlett1916_Notes=selected_copy.Bartlett1916_Notes,\
        Lee_Notes=selected_copy.Lee_Notes, Local_Notes=selected_copy.Local_Notes, created_by=selected_copy.created_by,\
        prov_info=selected_copy.prov_info, \
        librarian_validated=True, admin_validated=True, from_estc=False, false_positive=False, is_parent=True, is_history=False)

        #delete the child copy
        selected_copy.delete()

        data.append(model_to_dict(new_copy))

    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def admin_edit_titles(request):
    all_titles = Title.objects.all().order_by('title')
    template = loader.get_template('census/admin_edit_titles.html')
    queryset_list = Title.objects.all()
    query = request.GET.get("q")
    if query:
        queryset_list = queryset_list.filter(Q(title__icontains=query))
        paginator = Paginator(queryset_list, 10) # Show 10 titles per page
        page = request.GET.get('page')
        try:
            queryset_list = paginator.page(page)
        except PageNotAnInteger:
            #If page is not an integer, deliver first page.
            queryset_list = paginator.page(1)
        except EmptyPage:
            #If page is out of range, deliver last page of results.
            queryset_list = paginator.page(paginator.num_pages)
        context = {
            'query': query,
            'object_list': queryset_list,
        }

    else:
        paginator = Paginator(all_titles, 10) # Show 10 titles per page
        page = request.GET.get('page')
        try:
            titles = paginator.page(page)
        except PageNotAnInteger:
            #If page is not an integer, deliver first page.
            titles = paginator.page(1)
        except EmptyPage:
            #If page is out of range, deliver last page of results.
            titles = paginator.page(paginator.num_pages)

        context = {
            'object_list': queryset_list,
            'titles': titles,
        }

    return HttpResponse(template.render(context, request))

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

def copy_data(request, copy_id):
    template = loader.get_template('census/copy_modal.html')
    selected_copy=Copy.objects.get(pk=copy_id)
    context={"copy": selected_copy,}
    return HttpResponse(template.render(context, request))

def title_data(request, title_id):
    template = loader.get_template('census/title_modal.html')
    selected_title=Title.objects.get(pk=title_id)
    context={"title": selected_title,}
    return HttpResponse(template.render(context, request))

def edition_data(request, id):
    template = loader.get_template('census/edition_modal.html')
    print "here"
    selected_edition=Edition.objects.get(pk=id)
    context={"edition": selected_edition,}
    return HttpResponse(template.render(context, request))

def issue_data(request, issue_id):
    template = loader.get_template('census/issue_modal.html')
    selected_issue=Issue.objects.get(pk=issue_id)
    context={"issue": selected_issue,}
    return HttpResponse(template.render(context, request))

@login_required
def update_title (request, title_id):
    template=loader.get_template('census/title_update_modal.html')
    title_to_update = Title.objects.get(pk=title_id)
    data = {}
    if request.method=='POST':
        if request.POST.get('cancel', None):
            return HttpResponseRedirect(reverse('admin_edit_titles'))

        title_form=TitleForm(request.POST, instance=title_to_update)
        if title_form.is_valid():
            new_title=title_form.save()
            new_title.save(force_update=True)
            data['stat']="ok"
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            messages.error(request, 'Invalid title information!')
            data['stat'] = "copy error"

        title_form=TitleForm(data=request.POST)
        context = {
            'title_form': title_form,
            'title_id': title_id,
        }
        html=loader.render_to_string('census/title_update_modal.html', context, request=request)
        data['form']=html
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        title_form = TitleForm(instance=title_to_update)
        context = {
            'title_form': title_form,
            'title_id': title_id,
        }
        return HttpResponse(template.render(context, request))

@login_required
def update_edition(request, edition_id):
    template=loader.get_template('census/edition_update_modal.html')
    edition_to_update = Edition.objects.get(pk=edition_id)
    data = {}
    if request.method=='POST':
        if request.POST.get('cancel', None):
            return HttpResponseRedirect(reverse('admin_edit_titles'))

        edition_form=EditionForm(request.POST, instance=edition_to_update)
        if edition_form.is_valid():
            new_edition=edition_form.save()
            new_edition.save(force_update=True)
            data['stat']="ok"
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            messages.error(request, 'Invalid edition information!')
            data['stat'] = "copy error"

        edition_form=EditionForm(data=request.POST)
        context = {
            'edition_form': edition_form,
            'edition_id': edition_id,
        }
        html=loader.render_to_string('census/edition_update_modal.html', context, request=request)
        data['form']=html
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        edition_form = EditionForm(instance=edition_to_update)
        context = {
            'edition_form': edition_form,
            'edition_id': edition_id,
        }
        return HttpResponse(template.render(context, request))

@login_required
def update_issue(request, issue_id):
    template=loader.get_template('census/issue_update_modal.html')
    issue_to_update = Issue.objects.get(pk=issue_id)
    data = {}
    if request.method=='POST':
        if request.POST.get('cancel', None):
            return HttpResponseRedirect(reverse('admin_edit_titles'))

        issue_form=IssueForm(request.POST, instance=issue_to_update)
        if issue_form.is_valid():
            new_issue=issue_form.save()
            new_issue.save(force_update=True)
            data['stat']="ok"
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            messages.error(request, 'Invalid issue information!')
            data['stat'] = "copy error"

        issue_form=IssueForm(data=request.POST)
        context = {
            'issue_form': issue_form,
            'issue_id': issue_id,
        }
        html=loader.render_to_string('census/issue_update_modal.html', context, request=request)
        data['form']=html
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        issue_form = IssueForm(instance=issue_to_update)
        context = {
            'issue_form': issue_form,
            'issue_id': issue_id,
        }
        return HttpResponse(template.render(context, request))

@login_required()
def update_copy(request, copy_id):
    template = loader.get_template('census/edit_modal.html')
    all_titles = Title.objects.all()
    copy_to_edit=Copy.objects.get(pk=copy_id)
    old_issue=copy_to_edit.issue
    old_edition=old_issue.edition
    old_title=old_edition.title

    if request.method=='POST':
        data={}
        if request.POST.get('cancel', None):
            return HttpResponseRedirect(reverse('user_history'))

        issue_id=request.POST.get('issue')
        edition_id=request.POST.get('edition')
        title_id=request.POST.get('title')
        if not issue_id or issue_id == 'Z':
            issue_id = old_issue.id
            messages.error(request, 'Error: Please choose or add an issue!')
            data['stat']='issue error'
        elif not edition_id or edition_id == 'Z':
            edition_id = old_edition.id
            messages.error(request, 'Error: Please choose or add an edition!')
            data['stat']='edition error'
        elif not title_id or title_id == 'Z':
            title_id = old_title.id
            messages.error(request, 'Error: Please choose or add a title!')
            data['stat']='title error'
        else:
            selected_issue=Issue.objects.get(pk=issue_id)
            copy_form=CopyForm(data=request.POST)

            if copy_form.is_valid():
                new_copy=copy_form.save(commit=False)
                new_copy.issue = selected_issue
                new_copy.Owner = copy_to_edit.Owner

                # changes are made here
                new_copy.parent = copy_to_edit
                new_copy.is_parent=False
                new_copy.save()

                data['stat']="ok"
                return HttpResponse(json.dumps(data), content_type='application/json')

            else:
                messages.error(request, 'Invalid copy information!')
                data['stat'] = "copy error"

        copy_form=CopyForm(data=request.POST)
        selected_title=Title.objects.get(pk=title_id)
        selected_edition=Edition.objects.get(pk=edition_id)
        selected_issue=Issue.objects.get(pk=issue_id)

        context = {
                'all_titles': all_titles,
                'copy_form': copy_form,
                'copy_id': copy_id,
                'old_title_id': selected_title.id,
                'old_edition_set': selected_title.edition_set.all(),
                'old_edition_id': selected_edition.id,
                'old_issue_set': selected_edition.issue_set.all(),
                'old_issue_id': selected_issue.id,
                }
        html=loader.render_to_string('census/edit_modal.html', context, request=request)
        data['form']=html
        print(title_id)
        return HttpResponse(json.dumps(data), content_type='application/json')

    else:
        copy_form=CopyForm(instance=copy_to_edit)

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

@login_required()
def update_child_copy(request, copy_id):
    template = loader.get_template('census/edit_child_modal.html')
    copy_to_edit=ChildCopy.objects.get(pk=copy_id)

    if request.method=='POST':
        data={}
        if request.POST.get('cancel', None):
            return HttpResponseRedirect(reverse('user_history'))

        copy_form=ChildCopyForm(request.POST, instance=copy_to_edit)

        if copy_form.is_valid():
            new_copy=copy_form.save()
            new_copy.save(force_update=True)
            data['stat']="ok"
            return HttpResponse(json.dumps(data), content_type='application/json')

        else:
            messages.error(request, 'Invalid copy information!')
            data['stat'] = "copy error"

        copy_form=ChildCopyForm(data=request.POST)
        context = {
                'copy_form': copy_form,
                'copy_id': copy_id,
                }
        html=loader.render_to_string('census/edit_modal.html', context, request=request)
        data['form']=html
        return HttpResponse(json.dumps(data), content_type='application/json')

    else:
        copy_form=ChildCopyForm(instance=copy_to_edit)

    context = {
            'copy_form': copy_form,
            'copy_id': copy_id,
            }
    return HttpResponse(template.render(context, request))


#The functions below are not used right now.

#not used right now
def register(request):
    template = loader.get_template('census/register.html')
    if request.method == 'POST':
        user_form = LoginForm(data=request.POST)

        if user_form.is_valid():
            # save the new user
            new_user = User.objects.create_user(
                username=user_form.cleaned_data['username'],
                first_name=user_form.cleaned_data['first_name'],
                last_name=user_form.cleaned_data['last_name'],
                email=user_form.cleaned_data['email'],

                password=user_form.cleaned_data['password1'],
                )
            new_user.save()
            login(request, new_user)
            return HttpResponseRedirect("welcome")
        else:
            context = {
            'user_form.errors': user_form.errors,
            'user_form': user_form,
            }
            print(user_form.errors)
    else:
        user_form = LoginForm()
    return HttpResponse(template.render({'user_form': user_form}, request))

#need more infor for requirements; not used right now
def provenance(request):
    provenances= Provenance.objects.all()
    template = loader.get_template('census/provenance.html')
    context = {
        'provenances': provenances
    }
    return HttpResponse(template.render(context,request))

#need more infor for requirements; not used right now
def transactions(request, copy_id):
    selected_copy = Copy.objects.get(pk=copy_id)
    transactions= selected_copy.transaction_set.all()
    template = loader.get_template('census/transactions.html')
    context = {
        'transactions': transactions
    }
    return HttpResponse(template.render(context,request))

def get_icon_path(id):
    return 'census/images/title_icons/{}.png'.format(id)

#Showing issues related to a certain edition; not using right now
def issue(request, id):
    selected_edition = Edition.objects.get(pk=id)
    issues = selected_edition.issue_set.all()
    template = loader.get_template('census/issue.html')
    context = {
        'issues': issues,
        'selected_edition': selected_edition,
    }
    return HttpResponse(template.render(context, request))

#showing user history, not using right now
@login_required()
def user_history(request):
    template=loader.get_template('census/user_history.html')
    current_user=request.user
    copy_form=CopyForm()
    all_titles=Title.objects.all()
    all_submissions=current_user.submitted_copies.all().order_by('issue__start_date', 'issue__edition__title__title')
    paginator=Paginator(all_submissions, 10)
    page = request.GET.get('page')
    try:
        submissions = paginator.page(page)
    except PageNotAnInteger:
        submissions = paginator.page(1)
    except EmptyPage:
        copies = paginator.page(paginator.num_pages)
    cur_user_detail=UserDetail.objects.get(user=current_user)
    edited_copies=cur_user_detail.edited_copies.all()
    context={
        'submissions': submissions,
        'edited_copies': edited_copies,
        'all_titles': all_titles,
        'copy_form': copy_form,
    }
    return HttpResponse(template.render(context, request))

#showing the details of a copy, not using right now
def copy_detail(request, copy_id):
    template=loader.get_template('census/copy_detail.html')
    selected_copy=get_object_or_404(Copy, pk=copy_id)
    selected_issue=selected_copy.issue
    selected_edition=selected_issue.edition
    context={
        'selected_edition': selected_edition,
        'selected_copy': selected_copy,
    }
    return HttpResponse(template.render(context,request))
