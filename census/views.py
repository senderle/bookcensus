from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.template import loader
from . import models
from . import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.db.models import Q, Count, Sum #, Concat

from django.urls import reverse
from django.contrib import messages

from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.conf import settings

from datetime import datetime

import csv

## UTILITY FUNCTIONS ##
# Eventually these should be moved into a separate util module.
def get_or_create_draft(selected_copy):
    assert selected_copy.drafts.count() < 2, "There should not be more than one Draft copy"
    if not selected_copy.drafts.exists():
        models.create_draft(selected_copy)

    draft_copy = selected_copy.drafts.get()
    return draft_copy

def get_draft_if_exists(selected_copy):
    if not selected_copy.drafts.exists():
        return selected_copy
    else:
        return selected_copy.drafts.get()

def strip_article(s):
    articles = ['a ', 'A ', 'an ', 'An ', 'the ', 'The ']
    for a in articles:
        if s.startswith(a):
            return s.replace(a, '', 1)
    else:
        return s

def search_sort_date(copy):
    return (copy_date_sort_key(copy),
            title_sort_key(copy.issue.edition.title),
            copy_location_sort_key(copy))

def search_sort_title(copy):
    return (title_sort_key(copy.issue.edition.title),
            copy_date_sort_key(copy),
            copy_location_sort_key(copy))

def search_sort_location(copy):
    return (copy_location_sort_key(copy),
            copy_date_sort_key(copy),
            title_sort_key(copy.issue.edition.title))

def search_sort_stc(copy):
    return (copy.issue.STC_Wing,
            copy_location_sort_key(copy))

def copy_date_sort_key(c):
    return int(c.issue.start_date)

def copy_nsc_sort_key(c):
    nsc = c.NSC if c.NSC is not None else ''
    nsc_a = 0
    nsc_b = 0

    try:
        if '.' in nsc:
            nsc_a, nsc_b = nsc.split('.')
            nsc_a, nsc_b = int(nsc_a), int(nsc_b)
        else:
            nsc_a = int(nsc)
    except ValueError:
        pass

    return (nsc_a, nsc_b)

def copy_location_sort_key(c):
    if c.location is not None:
        name = c.location.name
    else:
        name = '' 
    return strip_article(name if name else '')

def copy_shelfmark_sort_key(c):
    sm = c.Shelfmark
    return sm if sm else ''

def copy_sort_key(c):
    sc_a, sc_b = copy_nsc_sort_key(c)
    return (copy_location_sort_key(c),
            copy_shelfmark_sort_key(c),
            sc_a,
            sc_b)

def title_sort_key(title_object):
    title = title_object.title
    if title == 'Comedies, Histories, and Tragedies':
        title = ' ' + title

    if title and title[0].isdigit():
        title = title.split()
        return strip_article(' '.join(title[1:] + [title[0]]))
    else:
        return strip_article(title)

def issue_sort_key(i):
    ed_number = i.edition.Edition_number
    ed_idx = int(ed_number) if ed_number.isdigit() else float('inf')
    return (ed_idx, i.STC_Wing)

def convert_year_range(year):
    if '-' in year:
        start, end = [n.strip() for n in year.split('-', 1)]
        if len(start) == 4 and start.isdigit() and len(end) == 4 and end.isdigit():
            return int(start), int(end)
    elif len(year) == 4 and year.isdigit():
        return int(year), int(year)
    return False

## VIEW FUNCTIONS ##

def search(request, field=None, value=None, order=None):
    template = loader.get_template('census/search-results.html')
    field = field if field is not None else request.GET.get('field')
    value = value if value is not None else request.GET.get('value')
    order = order if order is not None else request.GET.get('order')
    copy_list = models.CanonicalCopy.objects.all()
    display_field = field
    display_value = value

    if field == 'keyword' or field is None and value:
        field = 'keyword'
        display_field = 'Keyword Search'
        query = (Q(Marginalia__search=value) |
                 Q(Binding__search=value) |
                 Q(Binder__search=value) |
                 Q(Bookplate__search=value) |
                 Q(Bookplate_Location__search=value) |
                 Q(Bartlett1939_Notes__search=value) |
                 Q(Bartlett1916_Notes__search=value) |
                 Q(Lee_Notes__search=value) |
                 Q(rasmussen_west_notes__search=value) |
                 Q(Local_Notes__search=value) |
                 Q(prov_info__search=value) |
                 Q(bibliography__search=value) |
                 Q(provenance_search_names__name__search=value))
        result_list = copy_list.filter(query)
    elif field == 'stc' and value:
        display_field = 'STC / Wing'
        result_list = copy_list.filter(issue__STC_Wing__icontains=value)
    elif field == 'nsc' and value:
        display_field = 'SC'
        result_list = copy_list.filter(NSC=value)
    elif field == 'year' and value:
        display_field = 'Year'
        year_range = convert_year_range(value)
        if year_range:
            start, end = year_range
            result_list = copy_list.filter(issue__start_date__lte=end, issue__end_date__gte=start)
        else:
            result_list = copy_list.filter(issue__year__icontains=value)
    elif field == 'location' and value:
        display_field = 'Location'
        result_list = copy_list.filter(location__name__search=value)
    elif field == 'bartlett' and value:
        display_field = 'Bartlett'
        result_list = copy_list.filter(Q(Bartlett1916=value) | Q(Bartlett1939=value))
    elif field == 'provenance_name' and value:
        display_field = 'Provenance Name'
        result_list = copy_list.filter(provenance_search_names__name__search=value)
    elif field == 'unverified':
        display_field = 'Unverified'
        display_value = 'All'
        result_list = copy_list.filter(location_verified=False)
        if order is None:
            request.GET.order = 'location'
            order = 'location'
    elif field == 'ghosts':
        display_field = 'Ghosts'
        display_value = 'All'
        result_list = models.FalseCopy.objects.all()
    elif field == 'collection':
        result_list, display_field = get_collection(copy_list, value)
        display_value = 'All'
    else:
        result_list = models.CanonicalCopy.objects.none()

    result_list = result_list.exclude(issue__edition__title__title='Comedies, Histories, and Tragedies')
    result_list = result_list.distinct()

    if order is None:
        request.GET.order = 'date'
        result_list = sorted(result_list, key=search_sort_date)
    elif order == 'date':
        result_list = sorted(result_list, key=search_sort_date)
    elif order == 'title':
        result_list = sorted(result_list, key=search_sort_title)
    elif order == 'location':
        result_list = sorted(result_list, key=search_sort_location)
    elif order == 'stc':
        result_list = sorted(result_list, key=search_sort_stc)
    elif order == 'sc':
        result_list = sorted(result_list, key=copy_nsc_sort_key)

    context = {
        'icon_path': 'census/images/title_icons/generic-title-icon.png',
        'value': value,
        'field': field,
        'display_value': display_value,
        'display_field': display_field,
        'result_list': result_list,
        'copy_count': len(result_list)
    }

    return HttpResponse(template.render(context, request))

def get_collection(copy_list, coll_name):
    if coll_name == 'earlyprovenance':
        results = copy_list.filter(provenance_search_names__start_century='17')
        display = 'Copies with known early provenance (before 1700)'
    elif coll_name == 'womanowner':
        results = copy_list.filter(provenance_search_names__gender='F')
        display = 'Copies with a known woman owner'
    elif coll_name == 'earlywomanowner':
        results = copy_list.filter(Q(provenance_search_names__gender='F') &
                                   (Q(provenance_search_names__start_century='17') |
                                    Q(provenance_search_names__start_century='18')))
        display = 'Copies with a known woman owner before 1800'
    elif coll_name == 'marginalia':
        results = copy_list.exclude(Q(Marginalia='') | Q(Marginalia=None))
        display = 'Copies that include marginalia'
    elif coll_name == 'earlysammelband':
        results = copy_list.filter(in_early_sammelband=True)
        display = 'Copies in an early sammelband'

    return results, display

def autofill_collection(request, query=None):
    collection = [{'label': 'With known early provenance (before 1700)', 'value': 'earlyprovenance'},
                  {'label': 'With a known woman owner', 'value': 'womanowner'},
                  {'label': 'With a known woman owner before 1800', 'value': 'earlywomanowner'},
                  {'label': 'Includes marginalia', 'value': 'marginalia'},
                  {'label': 'In an early sammelband', 'value': 'earlysammelband'}]
    return JsonResponse({'matches': collection})

def autofill_location(request, query=None):
    if query is not None:
        location_matches = models.Location.objects.filter(name__icontains=query)
        match_object = {'matches': [m.name for m in location_matches]}
    else:
        match_object = {'matches': []}
    return JsonResponse(match_object)

def autofill_provenance(request, query=None):
    if query is not None:
        prov_matches = models.ProvenanceName.objects.filter(name__icontains=query)
        match_object = {'matches': [m.name for m in prov_matches]}
    else:
        match_object = {'matches': []}
    return JsonResponse(match_object)

def homepage(request):
    template = loader.get_template('census/frontpage.html')
    gridwidth = 5
    titlelist = models.Title.objects.all()
    if not request.user.is_staff:
        titlelist = titlelist.exclude(title='Comedies, Histories, and Tragedies')
    titlelist = sorted(titlelist, key=title_sort_key)
    titlerows = [titlelist[i: i + gridwidth]
                 for i in range(0, len(titlelist), gridwidth)]
    context = {
        'frontpage': True,
        'titlelist': titlelist,
        'titlerows': titlerows,
        'icon_path': 'census/images/title_icons/generic-title-icon.png'
    }
    return HttpResponse(template.render(context, request))

def about(request, viewname='about'):
    template = loader.get_template('census/about.html')

    copy_count = models.CanonicalCopy.objects.exclude(
        issue__edition__title__title='Comedies, Histories, and Tragedies'
    ).count()
    facsimile_copy_count = models.CanonicalCopy.objects.filter(
            ~Q(Digital_Facsimile_URL=None) & ~Q(Digital_Facsimile_URL='')
    ).count()
    facsimile_copy_percent = round(100 * facsimile_copy_count / copy_count)

    pre_render_context = {
        'copy_count': str(copy_count),
        'verified_copy_count': str(models.CanonicalCopy.objects.filter(location_verified=True).count()),
        'unverified_copy_count': str(models.CanonicalCopy.objects.filter(location_verified=False).count()),
        'current_date': '{d:%d %B %Y}'.format(d=datetime.now()),
        'facsimile_copy_count': str(facsimile_copy_count),
        'facsimile_copy_percent': '{}%'.format(facsimile_copy_percent),
        'estc_copy_count': str(models.CanonicalCopy.objects.filter(from_estc=True).count()),
        'non_estc_copy_count': str(models.CanonicalCopy.objects.filter(from_estc=False).count()),
    }
    content = [s.content.format(**pre_render_context)
               for s in models.StaticPageText.objects.filter(viewname=viewname)]

    context =  {
        'content': content,
    }
    return HttpResponse(template.render(context, request))

def detail(request, id):
    selected_title = get_object_or_404(models.Title, pk=id)
    if id == '5' or id == '6':
        editions = list(selected_title.edition_set.all())
        extra_ed = list(models.Title.objects.get(pk='39').edition_set.all())
        extra_ed[0].Edition_number = '3'
        editions.extend(extra_ed)
    else:
        editions = list(selected_title.edition_set.all())

    issues = [issue for ed in editions for issue in ed.issue_set.all()]
    issues.sort(key=issue_sort_key)
    copy_count = models.CanonicalCopy.objects.filter(issue__id__in=[i.id for i in issues]).count()
    template = loader.get_template('census/detail.html')
    context = {
        'icon_path': 'census/images/title_icons/generic-title-icon.png',
        'editions': editions,
        'issues': issues,
        'title': selected_title,
        'copy_count': copy_count,
    }
    return HttpResponse(template.render(context, request))

# showing all copies for an issue
def copy(request, id):
    selected_issue = get_object_or_404(models.Issue, pk=id)
    all_copies = models.CanonicalCopy.objects.filter(issue__id=id).order_by('location__name', 'Shelfmark')
    all_copies = sorted(all_copies, key=copy_sort_key)
    template = loader.get_template('census/copy.html')
    context = {
        'all_copies': all_copies,
        'copy_count': len(all_copies),
        'selected_issue': selected_issue,
        'icon_path': 'census/images/title_icons/generic-title-icon.png',
        'title': selected_issue.edition.title
    }
    return HttpResponse(template.render(context, request))

def draft_copy_data(request, copy_id):
    # This is a little bit questionable, so I'm explaining in detail.

    # To avoid having a proliferation of endpoints for copies of
    # multiple kinds, we simplify by assuming the incoming ID is
    # a canonical copy, and getting the corresponding draft
    # information if it exists. Otherwise, no draft has been created
    # yet, and so we should return the original data, which is the only
    # existing "draft."

    # That makes perfect sense.

    # *However* ... sometimes it's necessary to ask for an existing draft
    # copy by its own ID instead of by the copy id. If the above
    # fails, we try to do that instead. This allows us to reuse several
    # templates that we would otherwise have to customize.

    template = loader.get_template('census/copy_modal.html')
    selected_copy = models.CanonicalCopy.objects.filter(pk=copy_id)
    if selected_copy:
        selected_copy = get_draft_if_exists(selected_copy[0])
    else:
        selected_copy = models.DraftCopy.objects.get(pk=copy_id)

    context={"copy": selected_copy}

    return HttpResponse(template.render(context, request))

def copy_data(request, copy_id):
    # See above notes to `draft_copy_data`. Here, instead of
    # canonical -> draft, it's canonical -> false. But the essential
    # idea is the same; we get to reuse templates by cheating a
    # little bit here. In this case it's the `search_results`
    # template, which is also used to display false copies.

    template = loader.get_template('census/copy_modal.html')
    selected_copy = models.CanonicalCopy.objects.filter(pk=copy_id)
    if not selected_copy:
        selected_copy = models.FalseCopy.objects.filter(pk=copy_id)

    if selected_copy:
        selected_copy = selected_copy[0]
    else:
        raise Http404('Selected copy does not exist')

    context={"copy": selected_copy}

    return HttpResponse(template.render(context, request))

def sc_copy_modal(request, sc):
    # This is almost identical to copy, above, but it accepts a SC number
    # instead of an issue number, and if the SC number is found, it
    # finds the issue, and displays the page for that issue. The 
    # modal-display javascript then detects what has happened and
    # automatically displays the modal for the given copy.

    selected_copy = get_object_or_404(models.CanonicalCopy, NSC=sc)
    selected_issue = selected_copy.issue
    # all_copies = models.CanonicalCopy.objects.filter(issue=selected_issue).order_by('location__name', 'Shelfmark')
    # all_copies = sorted(all_copies, key=copy_sort_key)
    all_copies = [selected_copy]
    template = loader.get_template('census/copy.html')
    context = {
        'all_copies': all_copies,
        'copy_count': 0,
        'selected_issue': selected_issue,
        'icon_path': 'census/images/title_icons/generic-title-icon.png',
        'title': selected_issue.edition.title
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
                if user_account.is_staff:
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
    selected_copy = get_object_or_404(models.ChildCopy, pk=copy_id)
    selected_issue = selected_copy.issue
    selected_edition = selected_issue.edition
    context = {
        'selected_edition': selected_edition,
        'selected_copy': selected_copy,
    }
    return HttpResponse(template.render(context,request))

def location_copy_count_csv_export(request):
    locations = models.CanonicalCopy.objects.all().values('location')
    locations = locations.annotate(total=Count('location')).order_by('location__name')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shakespeare_census_location_copy_count.csv"'

    writer = csv.writer(response)
    writer.writerow(['Location', 'Number of Copies'])
    for loc in locations:
        writer.writerow([models.Location.objects.get(pk=loc['location']).name, loc['total']])

    return response

def year_issue_copy_count_csv_export(request):
    issues = models.CanonicalCopy.objects.exclude(
        issue__edition__title__title='Comedies, Histories, and Tragedies'
    ).values('issue')
    issues = issues.annotate(total=Count('issue')).order_by('issue__start_date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shakespeare_census_year_issue_copy_count.csv"'

    writer = csv.writer(response)
    writer.writerow(['Year', 'STC/Wing', 'Title', 'Number of Copies'])
    for iss in issues:
        iss_obj = models.Issue.objects.get(pk=iss['issue'])
        writer.writerow([
            iss_obj.start_date,
            iss_obj.STC_Wing,
            iss_obj.edition.title.title,
            iss['total']
        ])

    return response

def copy_sc_bartlett_csv_export(request):
    copies = models.CanonicalCopy.objects.exclude(
        issue__edition__title__title='Comedies, Histories, and Tragedies'
    )
    copies = copies.exclude(Bartlett1939=0, Bartlett1916=0)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shakespeare_census_year_issue_copy_count.csv"'

    writer = csv.writer(response)
    writer.writerow(['SC #', 'Bartlett 1939 #', 'Bartlett 1916 #', 'Title', 'Year'])
    for copy in copies:
        writer.writerow([
            copy.NSC,
            copy.Bartlett1939,
            copy.Bartlett1916,
            copy.issue.edition.title.title,
            copy.issue.start_date,
        ])

    return response

def export(request, groupby, column, aggregate):
    agg_model = (# Concat if aggregate == 'concatenation' else
                 Sum if aggregate == 'sum' else
                 Count)
    try:
        groups = models.CanonicalCopy.objects.all().values(groupby)
    except:
        raise Http404('Invalid groupby column.')

    try:
        rows = groups.annotate(agg=agg_model(column)).order_by(groupby)
    except:
        raise Http404('Invalid aggregation column.')

    filename = 'shakespeare_census_{}_of_{}_for_each_{}.csv'
    filename = filename.format(aggregate, column, groupby)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

    writer = csv.writer(response)
    writer.writerow([groupby, '{} of {}'.format(aggregate, column)])

    for row in rows:
        writer.writerow([row[groupby], row['agg']])

    return response

@login_required()
def add_copy(request, id):
    template = loader.get_template('census/copy_submission.html')
    selected_issue = models.Issue.objects.get(pk=id)

    data = {'issue_id': id, 'Shelfmark': '', 'Local_Notes': '', 'prov_info': ''}
    if request.method == 'POST':
        if request.user.is_staff:
            copy_submission_form = forms.AdminCopySubmissionForm(request.POST, initial=data)
        else:
            copy_submission_form = forms.LibrarianCopySubmissionForm(request.POST, initial=data)

        if copy_submission_form.is_valid():
            '''
            add draft
            linked to canonical_copy
            click to make prefilled word disappear
            move to the next page
            '''
            copy = copy_submission_form.save(commit=False)
            copy.location_verified = False
            if not request.user.is_staff:
                copy.location = models.UserDetail.objects.get(user=request.user).affiliation
                copy.location_verified = True
            copy.issue = models.Issue.objects.get(pk=id)
            copy.save()
            admin_notify()
            return HttpResponseRedirect(reverse('copy', args=(id,)))
    else:
        if request.user.is_staff:
            copy_submission_form = forms.AdminCopySubmissionForm(initial=data)
        else:
            copy_submission_form = forms.LibrarianCopySubmissionForm(initial=data)
    context = {
       'form': copy_submission_form,
       'issue': selected_issue,
       'icon_path': 'census/images/title_icons/generic-title-icon.png'
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
    cur_user_detail = models.UserDetail.objects.get(user=current_user)
    affiliation = cur_user_detail.affiliation

    copy_count = models.CanonicalCopy.objects.all().filter(location=affiliation,
                                                    location_verified=False).count()
    draft_count = models.DraftCopy.objects.all().filter(location=affiliation,
                                                        location_verified=True,
                                                        parent__location_verified=False).count()
    copy_count -= draft_count
    verified_count = models.CanonicalCopy.objects.all().filter(location=affiliation,
                                                        location_verified=True).count()
    verified_count += draft_count

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
    cur_user_detail = models.UserDetail.objects.get(user=current_user)
    affiliation = cur_user_detail.affiliation

    # Include all unverified records...
    copy_list = list(models.CanonicalCopy.objects.filter(location=affiliation, location_verified=False))

    # ...but filter out ones with drafts that have been verified.
    copy_list = [c for c in copy_list
                 if not c.drafts
                 or not c.drafts.first()
                 or not c.drafts.first().location_verified]

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
    cur_user_detail = models.UserDetail.objects.get(user=current_user)
    affiliation = cur_user_detail.affiliation

    # Include all verified drafts...
    verified_drafts = models.DraftCopy.objects.filter(location=affiliation,
                                                      location_verified=True)
    # And all verified copies...
    verified_copies = models.CanonicalCopy.objects.filter(location=affiliation,
                                                          location_verified=True)

    # ...but convert drafts to parents and add only those verified copies that
    # do not have drafts. (They would be included twice otherwise. Also...
    # TODO: To avoid an error, we have to drop drafts without parents. But
    #       in the long run, we'd like those to be editable. That is probably
    #       going to mean having a separate section -- there's just no clean
    #       way to get drafts and parents in the same section, sorted correctly.
    #       What I should do is have both sections on all views, and then have
    #       drafts and parents segregated, always. That will fix all the annoying
    #       problems we've been having.
    all_copies = [d.parent for d in verified_drafts if d.parent is not None] + [c for c in verified_copies if not c.drafts or not c.drafts.first()]

    all_copies = sorted(all_copies, key=librarian_validate_sort_key)
    context={
        'user_detail': cur_user_detail,
        'affiliation': affiliation.name,
        'child_copies': all_copies,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def update_draft_copy(request, id):
    template = loader.get_template('census/copy_submission.html')
    canonical_copy = models.CanonicalCopy.objects.get(pk=id)
    selected_copy = get_draft_if_exists(canonical_copy)

    init_fields = forms.LibrarianCopySubmissionForm.field_order
    data = {f: getattr(selected_copy, f) for f in init_fields}

    if request.method == 'POST':
        copy_form = forms.LibrarianCopySubmissionForm(request.POST)
    else:
        copy_form = forms.LibrarianCopySubmissionForm(initial=data)


    if request.method == 'POST' and copy_form.is_valid():
        copy_form_data = copy_form.save(commit=False)
        draft_copy = get_or_create_draft(canonical_copy)
        for f in init_fields:
            setattr(draft_copy, f, getattr(copy_form_data, f))
        draft_copy.save()
        admin_notify()
        return HttpResponseRedirect(reverse('librarian_validate2'))
    else:
        context = {
            'form': copy_form,
            'copy': selected_copy,
            'icon_path': 'census/images/title_icons/generic-title-icon.png'
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
    selected_copies = models.DraftCopy.objects.all()
    copies = [copy for copy in selected_copies
              if copy.parent and
                 isinstance(copy.parent, models.CanonicalCopy) and
                 copy.parent.location_verified]

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
def admin_submission_verify(request):
    template = template = loader.get_template('census/staff/admin_submission_verify.html')
    selected_copies = models.DraftCopy.objects.all()
    copies = [copy for copy in selected_copies
              if not copy.parent]

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
    copy_id = request.GET.get('copy_id')

    selected_draft_copy = models.DraftCopy.objects.get(pk=copy_id)
    if selected_draft_copy.parent and isinstance(selected_draft_copy.parent, models.CanonicalCopy):
        models.draft_to_canonical_update(selected_draft_copy)
    else:
        models.draft_to_canonical_create(selected_draft_copy)

    return HttpResponse('success')

@login_required
def admin_verify_single_edit_reject(request):
    copy_id = request.GET.get('copy_id')

    selected_draft_copy = models.DraftCopy.objects.get(pk=copy_id)
    models.draft_to_reject_move(selected_draft_copy)

    return HttpResponse('success')

@login_required
def admin_verify_location_verified(request):
    template = loader.get_template('census/staff/admin_verify.html')
    selected_copies = models.DraftCopy.objects.all()
    copies = [copy for copy in selected_copies
              if copy.parent and
                 isinstance(copy.parent, models.CanonicalCopy) and not
                 copy.parent.location_verified]

    context={
        'copies': copies
    }
    return HttpResponse(template.render(context, request))

# This is for verifying copy location.
@login_required()
def admin_verify_copy(request):
    copy_id = request.GET.get('copy_id')

    try:
        selected_draft_copy = models.DraftCopy.objects.get(pk=copy_id)
    except models.DraftCopy.DoesNotExist:
        raise Http404("No draft matches the query.")
    canonical_copy = selected_draft_copy.parent

    if not selected_draft_copy.location_verified:
        selected_draft_copy.delete()
        models.canonical_to_fp_move(canonical_copy)
    else:
        # We directly edit the canonical copy here and create a history
        # record for it, without touching the draft, because we need to
        # verify the edits separately. This means that in cases where the
        # librarian has made no edits, this will still appear in the admin
        # edit verify queue. I am not sure about the best way to handle this.
        models.create_history(canonical_copy)
        canonical_copy.location_verified = True
        canonical_copy.save()

    return HttpResponse('success')

@login_required()
def edit_profile(request):
    template=loader.get_template('census/edit_profile.html')
    current_user=request.user
    if request.method=='POST':
        profile_form = forms.EditProfileForm(request.POST, instance=current_user)
        if profile_form.is_valid():
            profile_form.save()
            return HttpResponseRedirect(reverse('profile'))
        else:
            messages.error(request, "That username is already taken.")
    else:
        profile_form=forms.EditProfileForm(instance=current_user)

    context={
        'user': current_user,
        'profile_form': profile_form,
    }
    return HttpResponse(template.render(context, request))

#used by aja
@login_required
def create_draftcopy(request):
    copy_id = request.GET.get('copy_id')

    selected_copy =  models.CanonicalCopy.objects.get(pk=copy_id)
    draft_copy = get_or_create_draft(selected_copy)
    draft_copy.location_verified = True
    draft_copy.save()
    admin_notify()

    return HttpResponse("success!")

@login_required
def location_incorrect(request):
    copy_id = request.GET.get('copy_id')

    selected_copy =  models.CanonicalCopy.objects.get(pk=copy_id)
    draft_copy = get_or_create_draft(selected_copy)
    draft_copy.location_verified = False
    draft_copy.save()
    admin_notify()

    return HttpResponse("success!")

def signup(request):
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user_detail = models.UserDetail(user=user)
            user_detail.affiliation = form.cleaned_data['affiliation']
            user_detail.save()
            admin_notify()

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
        form = forms.SignupForm()

    return render(request, 'signup/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user_detail = models.UserDetail.objects.get(user=user)
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

def admin_notify():
    # message = render_to_string('signup/acc_active_email.html', {
    #     'user':user,
    #     'domain':current_site.domain,
    #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
    #     'token': account_activation_token.make_token(user),
    # })
    emails = [email for name, email in settings.NOTIFICATIONS]
    message = 'There is a new user submission awaiting admin attenion.'
    mail_subject = 'Shakespeare Census user activity'
    message = EmailMessage(mail_subject, message, to=emails)
    message.send()

def contact(request):
    template=loader.get_template('census/contact-form.html')

    if request.method=='POST':
        form = forms.ContactUs(request.POST)
        if form.is_valid() and form.data['guardian'] == "":
            form.save()
            admin_notify()
            return HttpResponseRedirect(reverse('contact_success'))
        elif form.is_valid() and form.data['guardian'] != "":
            return HttpResponseRedirect(reverse('contact_success'))
        else:
            messages.error(request, "This form is invalid")
    else:
        form = forms.ContactUs()

    context={'form': form}
    return HttpResponse(template.render(context, request))

def display_contact_success(request):
    template = loader.get_template('census/contact-form-success.html')
    current_user = request.user
    context = {
        'user': current_user,
    }
    return HttpResponse(template.render(context, request))


@login_required
def enter_copy(request):
    if request.method == 'POST':
        form = forms.EnterCopyForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Success!")
    else:
        form = forms.EnterCopyForm()

    return render(request, 'census/staff/enter_copy.html', {'form': form})
