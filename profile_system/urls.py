from django.conf.urls import url
from . import views

urlpatterns = [
    # Main pages
    url(r'^$', views.home, name='home'),
    url(r'^register/$', views.register, name='register'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    
    # Profile management
    url(r'^profile/create/$', views.create_profile, name='create_profile'),
    url(r'^profile/(?P<gsez_id>[\w-]+)/$', views.profile_detail, name='profile_detail'),
    url(r'^profile/(?P<gsez_id>[\w-]+)/edit/$', views.edit_profile, name='edit_profile'),
    
    # Profile creation steps
    url(r'^profile/family-details/$', views.add_family_details, name='add_family_details'),
    url(r'^profile/family_details/$', views.add_family_details, name='add_family_details_alt'),  # Alternative URL
    url(r'^profile/address/$', views.add_address, name='add_address'),
    url(r'^profile/permanent-address/$', views.add_permanent_address, name='add_permanent_address'),
    url(r'^profile/education/$', views.add_education, name='add_education'),
    url(r'^profile/employment/$', views.add_employment, name='add_employment'),
    
    # Job portal
    url(r'^jobs/$', views.job_list, name='job_list'),
    url(r'^jobs/(?P<job_id>\d+)/$', views.job_detail, name='job_detail'),
    
    # Company management
    url(r'^company/dashboard/$', views.company_dashboard, name='company_dashboard'),
    url(r'^company/jobs/create/$', views.create_job_posting, name='create_job_posting'),
    url(r'^company/jobs/(?P<job_id>\d+)/applications/$', views.job_applications, name='job_applications'),
    
    # Security features
    url(r'^scan-qr/$', views.scan_qr, name='scan_qr'),
    url(r'^profile/(?P<gsez_id>[\w-]+)/log-access/$', views.log_access, name='log_access'),
    url(r'^search-profiles/$', views.search_profiles, name='search_profiles'),
] 