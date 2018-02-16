from django.conf.urls import url, include
from django.contrib.auth.views import (password_reset,
                                       password_reset_done,
                                       password_reset_confirm,
                                       password_reset_complete,
                                       logout)

from . import views

urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^editions/(?P<id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^about', views.about, name='about'),

    url(r'^titles', views.index, name='index'),
    url(r'^copy/(?P<id>[0-9]+)/$', views.copy, name='copy'),
    url(r'^copies', views.copylist, name='copylist'),
    url(r'^issue/(?P<id>[0-9]+)/$', views.issue, name='issue'),
    url(r'^provenance$', views.provenance, name='provenance'),
    # url(r'^register$', views.register, name='register'),

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

    url(r'^login', views.login_user, name='login_user'),
    url(r'^accounts/login/$', views.login_user, name='login_user'),
    url(r'^logout$', views.logout_user, name='logout_user'),
    url(r'^homepage$',views.homepage, name='homepage'),
    url(r'^search/$', views.search, name='search_for_something'),

    #for viewing user's profile
    url(r'^profile$', views.display_user_profile, name='profile'),

    #for viewing user's history (submitted copies & editted copies)
    url(r'^user_history$', views.user_history, name='user_history'),

    url(r'^librarian_confirm/(?P<id>[0-9]+)/$', views.librarian_confirm, name='librarian_validate'),

    url(r'^admin_verify$', views.admin_verify, name='admin_verify'), #to verify changes to copies
    url(r'^admin_verify_fp$', views.admin_verify_fp, name='admin_verify_fp'), #to verify false_positive_draft

    #button triggered, change false_positive attribute of the copy
    url(r'^admin_verify_copy_fp/(?P<copy_id>[0-9]+)/$', views.admin_verify_copy_fp, name='admin_verify_copy_fp'),

    #button triggered, change admin_validated attribute of the copy
    url(r'^admin_verify_copy/(?P<id>[0-9]+)/$', views.admin_verify_copy, name='admin_verify_copy'),


    url(r'^admin_edit_titles$', views.admin_edit_titles, name='admin_edit_titles'),
    url(r'^admin_start$', views.admin_start, name='admin_start'),

    url(r'^librarian_validate1$', views.librarian_validate1, name='librarian_validate1'),
    url(r'^validate_hold/(?P<id>[0-9]+)/$', views.validate_hold, name='validate_hold'),
    url(r'^validate_not_hold/(?P<id>[0-9]+)/$', views.validate_not_hold, name='validate_not_hold'),
    url(r'^change_hold_status/(?P<id>[0-9]+)/$', views.change_hold_status, name='change_hold_status'),
    url(r'^librarian_validate2$', views.librarian_validate2, name='librarian_validate2'),
    url(r'^librarian_start$', views.librarian_start, name='librarian_start'),
    url(r'^change_false_positive_draft/(?P<id>[0-9]+)/$', views.change_false_positive_draft, name='change_false_positive_draft'),
    url(r'^editProfile$', views.edit_profile, name='edit_profile'),

    url(r'^copydata/(?P<copy_id>[0-9]+)/$', views.copy_data, name='copy_data'),
    url(r'^titledata/(?P<title_id>[0-9]+)/$', views.title_data, name='title_data'),
    url(r'^editiondata/(?P<id>[0-9]+)/$', views.edition_data, name='edition_data'),
    url(r'^issuedata/(?P<issue_id>[0-9]+)/$', views.issue_data, name='issue_data'),
    url(r'^updatetitle/(?P<title_id>[0-9]+)/$', views.update_title, name='update_title'),
    url(r'^updateedition/(?P<edition_id>[0-9]+)/$', views.update_edition, name='update_edition'),
    url(r'^updateissue/(?P<issue_id>[0-9]+)/$', views.update_issue, name='update_issue'),

    url(r'^updatecopy/(?P<copy_id>[0-9]+)/$', views.update_copy, name='update_copy'),
    url(r'^updatechildcopy/(?P<copy_id>[0-9]+)/$', views.update_child_copy, name='update_child_copy'),

    url(r'^password_reset/$', password_reset,
        {'template_name': 'census/password_reset_form.html',
         'email_template_name': 'census/password_reset_email.html',
         'subject_template_name': 'census/password_reset_subject.txt'},
        name='password_reset'),
    url(r'^user/password_reset_done/$', password_reset_done,
        {'template_name': 'census/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^user/password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        '(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm,
        {'template_name': 'census/password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^user/password_reset/complete/$', password_reset_complete,
        {'template_name': 'census/password_reset_complete.html'},
        name='password_reset_complete'),
]
