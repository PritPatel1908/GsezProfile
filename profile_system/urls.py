from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('custom-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/roles/', views.role_management, name='role_management'),
    
    # Profile management
    path('profile/create/', views.create_profile, name='create_profile'),
    path('profile/wizard/', views.profile_wizard, name='profile_wizard'),
    path('profile/skip/', views.skip_profile, name='skip_profile'),
    path('profile/<str:gsez_id>/', views.profile_detail, name='profile_detail'),
    path('profile/<str:gsez_id>/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:gsez_id>/verify/', views.verify_profile, name='verify_profile'),
    
    # Profile creation steps
    path('profile/<str:gsez_id>/family-details/add/', views.add_family_details, name='add_family_details'),
    path('profile/<str:gsez_id>/family-details/', views.family_details, name='family_details'),
    path('profile/<str:gsez_id>/family-details/<int:family_id>/edit/', views.edit_family_detail, name='edit_family_detail'),
    path('profile/<str:gsez_id>/family-details/<int:family_id>/delete/', views.delete_family_detail, name='delete_family_detail'),
    
    path('profile/<str:gsez_id>/address/add/', views.add_address, name='add_address'),
    path('profile/<str:gsez_id>/addresses/', views.addresses, name='addresses'),
    path('profile/<str:gsez_id>/address/<int:address_id>/edit/', views.edit_address, name='edit_address'),
    path('profile/<str:gsez_id>/address/<int:address_id>/delete/', views.delete_address, name='delete_address'),
    
    path('profile/<str:gsez_id>/education/add/', views.add_education, name='add_education'),
    path('profile/<str:gsez_id>/education/', views.education, name='education'),
    path('profile/<str:gsez_id>/education/<int:education_id>/edit/', views.edit_education, name='edit_education'),
    path('profile/<str:gsez_id>/education/<int:education_id>/delete/', views.delete_education, name='delete_education'),
    
    path('profile/<str:gsez_id>/employment/add/', views.add_employment, name='add_employment'),
    path('profile/<str:gsez_id>/employment/', views.employment, name='employment'),
    path('profile/<str:gsez_id>/employment/<int:employment_id>/edit/', views.edit_employment, name='edit_employment'),
    path('profile/<str:gsez_id>/employment/<int:employment_id>/delete/', views.delete_employment, name='delete_employment'),
    
    # Job portal
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    
    # Company management
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/jobs/create/', views.create_job_posting, name='create_job_posting'),
    path('company/jobs/<int:job_id>/applications/', views.job_applications, name='job_applications'),
    
    # Security features
    path('scan-qr/', views.scan_qr, name='scan_qr'),
    path('profile/<str:gsez_id>/log-access/', views.log_access, name='log_access'),
    path('search-profiles/', views.search_profiles, name='search_profiles'),
    
    # Admin Panel - User Management
    path('custom-admin/users/', views.admin_users, name='admin_users'),
    path('custom-admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('custom-admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('custom-admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('custom-admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('custom-admin/users/<int:user_id>/password/', views.admin_user_password, name='admin_user_password'),
    path('custom-admin/users/<int:user_id>/permissions/', views.admin_user_permissions, name='admin_user_permissions'),
    path('custom-admin/users/<int:user_id>/toggle-active/', views.admin_user_toggle_active, name='admin_user_toggle_active'),
    
    # Admin Panel - Profile Management
    path('custom-admin/profiles/', views.admin_profiles, name='admin_profiles'),
    path('custom-admin/profiles/create/', views.admin_profile_create, name='admin_profile_create'),
    path('custom-admin/users/<int:user_id>/create-profile/', views.admin_create_profile, name='admin_create_profile'),
    path('custom-admin/profiles/<int:profile_id>/status/<str:status>/', views.admin_profile_status, name='admin_profile_status'),
    path('custom-admin/profiles/<int:profile_id>/delete/', views.admin_profile_delete, name='admin_profile_delete'),
    
    # Admin Panel - Company Management
    path('custom-admin/companies/', views.admin_companies, name='admin_companies'),
    path('custom-admin/companies/create/', views.admin_company_create, name='admin_company_create'),
    path('custom-admin/companies/<int:company_id>/', views.admin_company_view, name='company_detail'),
    path('custom-admin/companies/<int:company_id>/edit/', views.admin_company_edit, name='edit_company'),
    path('custom-admin/companies/<int:company_id>/delete/', views.admin_company_delete, name='admin_company_delete'),
    path('custom-admin/companies/<int:company_id>/employees/', views.admin_company_employees, name='company_employees'),
    path('custom-admin/companies/<int:company_id>/jobs/', views.admin_company_jobs, name='admin_company_jobs'),
    path('custom-admin/companies/<int:company_id>/status/<str:status>/', views.admin_company_status, name='admin_company_status'),
    
    # Admin Panel - Job Management
    path('custom-admin/jobs/', views.admin_jobs, name='admin_jobs'),
    path('custom-admin/jobs/create/', views.admin_job_create, name='admin_job_create'),
    path('custom-admin/jobs/<int:job_id>/edit/', views.admin_job_edit, name='admin_job_edit'),
    path('custom-admin/jobs/<int:job_id>/delete/', views.admin_job_delete, name='admin_job_delete'),
    path('custom-admin/jobs/<int:job_id>/toggle-status/', views.admin_job_toggle_status, name='admin_job_toggle_status'),
    path('custom-admin/jobs/<int:job_id>/applications/', views.admin_job_applications, name='admin_job_applications'),
] 