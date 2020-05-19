from django.conf.urls import url

from . import views

# from .models import StaticPageText
# _static_page_names = '|'.join(sorted(set(s.viewname for s in StaticPageText.objects.all())))

urlpatterns = [
    # Main site functionality
    url(r'^$', views.homepage, name='homepage'),
    url(r'^$', views.homepage, name='home'),
    url(r'^homepage$', views.homepage, name='homepage'),
    url(r'^search/$', views.search, name='search'),
    url(r'^search/(?P<field>[A-Za-z0-9- ]+)/(?P<value>[A-Za-z0-9- ]+)/$', views.search, name='search'),
    url(r'^search/(?P<field>[A-Za-z0-9- ]+)/(?P<value>[A-Za-z0-9- ]+)/(?P<order>[A-Za-z0-9- ]+)/$',
        views.search, name='search'),
    url(r'^editions/(?P<id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^about/$', views.about, name='about'),
    url(r'^about/(?P<viewname>[A-Za-z0-9-]+)/$', views.about, name='about'),
    url(r'^copy/(?P<id>[0-9]+)/$', views.copy, name='copy'),
    url(r'^copydata/(?P<copy_id>[0-9]+)/$', views.copy_data, name='copy_data'),
    url(r'^sc/(?P<sc>[0-9.]+)/$', views.sc_copy_modal, name='sc_copy_modal'),
    url(r'^draftcopydata/(?P<copy_id>[0-9]+)/$', views.draft_copy_data, name='draft_copy_data'),
    url(r'^add_copy/(?P<id>[0-9]+)/$', views.add_copy, name='add_copy'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^contact/contact_success/$', views.display_contact_success, name='contact_success'),

    # Search autocomplete
    url(r'^autofill/location/$', views.autofill_location, name='autofill_location'),
    url(r'^autofill/location/(?P<query>[A-Za-z0-9- ]+)/$', views.autofill_location, name='autofill_location'),
    url(r'^autofill/provenance/$', views.autofill_provenance, name='autofill_provenance'),
    url(r'^autofill/provenance/(?P<query>[A-Za-z0-9- ]+)/$', views.autofill_provenance, name='autofill_provenance'),
    url(r'^autofill/collection/$', views.autofill_collection, name='autofill_collection'),
    url(r'^autofill/collection/(?P<query>[A-Za-z0-9- ]+)/$', views.autofill_collection, name='autofill_collection'),

    # Data export
    url(r'^location_copy_count_csv_export/$',
        views.location_copy_count_csv_export,
        name='location_copy_count_csv_export'),
    url(r'^year_issue_copy_count_csv_export/$',
        views.year_issue_copy_count_csv_export,
        name='year_issue_copy_count_csv_export'),
    url(r'^copy_sc_bartlett_csv_export/$',
        views.copy_sc_bartlett_csv_export,
        name='copy_sc_bartlett_csv_export'),
    url(r'^export/(?P<groupby>[A-Za-z0-9_]{1,50})/(?P<column>[A-Za-z0-9_]{1,50})/(?P<aggregate>[A-Za-z0-9_]{1,50})/$',
        views.export, name='export'),

    # User accounts and management
    url(r'^login', views.login_user, name='login_user'),
    url(r'^logout$', views.logout_user, name='logout_user'),
    url(r'^profile$', views.display_user_profile, name='profile'),
    url(r'^editProfile$', views.edit_profile, name='edit_profile'),

    # Librarian verification and admin approval routines.

    # Admin start page:
    url(r'^admin_start$', views.admin_start, name='admin_start'),

    # Location verification page:
    url(r'^admin_verify_copy/$', views.admin_verify_copy, name='admin_verify_copy'),
    # ...and ajax call
    url(r'^admin_verify_location_verified$', views.admin_verify_location_verified, name='admin_verify_location_verified'),

    # Edit verification and submission verification pages:
    url(r'^admin_edit_verify$', views.admin_edit_verify, name='admin_edit_verify'),
    url(r'^admin_submission_verify$', views.admin_submission_verify, name='admin_submission_verify'),
    # ...and ajax calls
    url(r'^admin_verify_single_edit_accept/$', views.admin_verify_single_edit_accept, name='admin_verify_single_edit_accept'),
    url(r'^admin_verify_single_edit_reject/$', views.admin_verify_single_edit_reject, name='admin_verify_single_edit_reject'),

    # Librarian-specific verification UI elements:
    url(r'^librarian_start$', views.librarian_start, name='librarian_start'),
    url(r'^librarian_validate1$', views.librarian_validate1, name='librarian_validate1'),
    url(r'^librarian_validate2$', views.librarian_validate2, name='librarian_validate2'),
    url(r'^updatedraftcopy/(?P<id>[0-9]+)/$', views.update_draft_copy, name='update_draft_copy'),

    # url for the ajax view that creates the new draftcopy
    url(r'^create_draftcopy/$',views.create_draftcopy, name='create_draftcopy'),
    url(r'^location_incorrect/$',views.location_incorrect, name='location_incorrect'),

    url(r'^signup/$', views.signup, name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),

    # url for entering copies
    url(r'^enter_copy', views.enter_copy, name='enter_copy'),
]
