from django.conf.urls import url, include
from django.contrib.auth.views import (password_reset,
                                       password_reset_done,
                                       password_reset_confirm,
                                       password_reset_complete,
                                       password_change,
                                       password_change_done,
                                       logout)

from . import views

# from .models import StaticPageText
# _static_page_names = '|'.join(sorted(set(s.viewname for s in StaticPageText.objects.all())))

urlpatterns = [
    # Main site functionality
    url(r'^$', views.homepage, name='homepage'),
    url(r'^homepage$',views.homepage, name='homepage'),
    url(r'^search/$', views.search, name='search_for_something'),
    url(r'^editions/(?P<id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^about/$', views.about, name='about'),
    # url(r'^about/(?P<viewname>' + _static_page_names + ')/$', views.about, name='about'),
    url(r'^about/(?P<viewname>[A-Za-z0-9]+)/$', views.about, name='about'),
    url(r'^copy/(?P<id>[0-9]+)/$', views.copy, name='copy'),
    url(r'^copydata/(?P<copy_id>[0-9]+)/$', views.copy_data, name='copy_data'),
    url(r'^admincopydata/(?P<id>[0-9]+)/$', views.admin_copy_data, name='admin_copy_data'),
    url(r'^add_copy/(?P<id>[0-9]+)/$', views.add_copy, name='add_copy'),

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
    url(r'^librarian_register/$', views.register, name='register'),
    url(r'^logout$', views.logout_user, name='logout_user'),
    url(r'^profile$', views.display_user_profile, name='profile'),
    url(r'^editProfile$', views.edit_profile, name='edit_profile'),

    # Librarian verification and admin approval routines.

    url(r'^admin_verify_location_verified$', views.admin_verify_location_verified, name='admin_verify_location_verified'), #to verify false_positive_draft
    #button triggered, change false_positive attribute of the copy

    #button triggered, change admin_validated attribute of the copy
    url(r'^admin_edit_verify$', views.admin_edit_verify, name='admin_edit_verify'),
    url(r'^admin_verify_single_edit_accept/$', views.admin_verify_single_edit_accept, name='admin_verify_single_edit_accept'),
    url(r'^admin_verify_single_edit_reject/$', views.admin_verify_single_edit_reject, name='admin_verify_single_edit_reject'),
    url(r'^admin_verify_copy/$', views.admin_verify_copy, name='admin_verify_copy'),
    url(r'^admin_start$', views.admin_start, name='admin_start'),

    # Librarian-specific verification UI elements:
    url(r'^librarian_start$', views.librarian_start, name='librarian_start'),
    url(r'^librarian_validate1$', views.librarian_validate1, name='librarian_validate1'),
    url(r'^librarian_validate2$', views.librarian_validate2, name='librarian_validate2'),
    url(r'^updatedraftcopy/(?P<id>[0-9]+)/$', views.update_draft_copy, name='update_draft_copy'),

    # url for the ajax view that creates the new draftcopy
    url(r'^create_draftcopy/$',views.create_draftcopy, name='create_draftcopy'),
    url(r'^location_incorrect/$',views.location_incorrect, name='location_incorrect'),

    #url for password change
    url(r'^librarian_password_change/$', password_change, {
        'template_name': 'registration/password_change_form.html'},
        name='password_change'),
    url(r'^accounts/password/change/done/$', password_change_done,
        {'template_name': 'registration/password_change_done.html'},
        name='password_change_done'),

]
