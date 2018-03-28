from django.conf.urls import url, include
from django.contrib.auth.views import (password_reset,
                                       password_reset_done,
                                       password_reset_confirm,
                                       password_reset_complete,
                                       logout)

from . import views
from .models import StaticPageText

_static_page_names = '|'.join(sorted(set(s.viewname for s in StaticPageText.objects.all())))

urlpatterns = [
    # Main site functionality
    url(r'^$', views.homepage, name='homepage'),
    url(r'^homepage$',views.homepage, name='homepage'),
    url(r'^search/$', views.search, name='search_for_something'),
    url(r'^editions/(?P<id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^about/$', views.about, name='about'),
    url(r'^about/(?P<viewname>' + _static_page_names + ')/$', views.about, name='about'),
    url(r'^copy/(?P<id>[0-9]+)/$', views.copy, name='copy'),
    url(r'^copydata/(?P<copy_id>[0-9]+)/$', views.copy_data, name='copy_data'),

    # Jinyun-urls for submission forms
    url(r'^submission$', views.submission, name='submission'),
    url(r'^title/(?P<id>[0-9]+)/$', views.json_editions, name='json_editions'),
    url(r'^edition/(?P<id>[0-9]+)/$', views.json_issues, name='json_issues'),
    url(r'^addTitle$', views.add_title, name='add_title'),
    url(r'^addEdition/(?P<title_id>[0-9]+)/$', views.add_edition, name='add_edition'),
    url(r'^addIssue/(?P<edition_id>[0-9]+)/$', views.add_issue, name='add_issue'),

    #reviewing submitted copy-info, having edit, confirm, and cancel buttons
    url(r'^copy_info/(?P<copy_id>[0-9]+)/$', views.copy_info, name='copy_info'),
    url(r'^copysubmissionsuccess$', views.copy_submission_success, name='copy_success'),
    url(r'^cancelcopysubmission/(?P<copy_id>[0-9]+)/$', views.cancel_copy_submission, name='cancel_copy_submission'),
    url(r'^editcopysubmission/(?P<copy_id>[0-9]+)/$', views.edit_copy_submission, name='edit_copy_submission'),

    # User accounts and management
    url(r'^login', views.login_user, name='login_user'),
    url(r'^accounts/login/$', views.login_user, name='login_user'),
    url(r'^logout$', views.logout_user, name='logout_user'),
    url(r'^profile$', views.display_user_profile, name='profile'),

    #for viewing user's history (submitted copies & editted copies)
    url(r'^librarian_confirm/(?P<id>[0-9]+)/$', views.librarian_confirm, name='librarian_validate'),
    url(r'^admin_verify$', views.admin_verify, name='admin_verify'), #to verify changes to copies
    url(r'^admin_verify_fp$', views.admin_verify_fp, name='admin_verify_fp'), #to verify false_positive_draft

    #button triggered, change false_positive attribute of the copy
    url(r'^admin_verify_copy_fp/(?P<copy_id>[0-9]+)/$', views.admin_verify_copy_fp, name='admin_verify_copy_fp'),

    #button triggered, change admin_validated attribute of the copy
    url(r'^admin_verify_copy/(?P<id>[0-9]+)/$', views.admin_verify_copy, name='admin_verify_copy'),

    url(r'^admin_start$', views.admin_start, name='admin_start'),

    url(r'^librarian_validate1$', views.librarian_validate1, name='librarian_validate1'),
    url(r'^validate_hold/(?P<id>[0-9]+)/$', views.validate_hold, name='validate_hold'),
    url(r'^validate_not_hold/(?P<id>[0-9]+)/$', views.validate_not_hold, name='validate_not_hold'),
    url(r'^change_hold_status/(?P<id>[0-9]+)/$', views.change_hold_status, name='change_hold_status'),
    url(r'^librarian_validate2$', views.librarian_validate2, name='librarian_validate2'),
    url(r'^librarian_start$', views.librarian_start, name='librarian_start'),
    url(r'^change_false_positive_draft/(?P<id>[0-9]+)/$', views.change_false_positive_draft, name='change_false_positive_draft'),
    url(r'^editProfile$', views.edit_profile, name='edit_profile'),

]
