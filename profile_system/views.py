from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    Profile, FamilyDetail, Address, Company, 
    Employment, Education, JobPosting, JobApplication, AccessLog, UserRole
)
from .forms import (
    UserRegistrationForm, ProfileForm, FamilyDetailForm, 
    AddressForm, CompanyForm, EmploymentForm, EducationForm,
    JobPostingForm, JobApplicationForm, ProfileSearchForm, JobSearchForm, UserRoleForm, ProfileVerificationForm
)
from django.core.paginator import Paginator

@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Check if admin skipped profile creation
    if 'skip_profile' in request.GET:
        try:
            # Check if profile exists
            profile = request.user.profile
        except Profile.DoesNotExist:
            # Show message that profile creation was skipped
            messages.info(request, 'You have skipped profile creation. You can create your profile later if needed.')
    
    # Get statistics
    user_count = User.objects.count()
    company_count = Company.objects.count()
    profile_count = Profile.objects.count()
    job_count = JobPosting.objects.filter(is_active=True).count()
    
    # Calculate growth percentages (mock data for now)
    user_growth = 12
    profile_growth = 18
    company_growth = 8
    job_growth = 15
    
    # Get active users count (mock data)
    active_users_count = 24
    
    # Get recent data
    recent_users = User.objects.all().select_related('user_role').order_by('-date_joined')[:5]
    recent_profiles = Profile.objects.all().order_by('-issue_date')[:5]
    recent_jobs = JobPosting.objects.all().order_by('-posted_date')[:5]
    recent_access_logs = AccessLog.objects.all().order_by('-timestamp')[:5]
    
    # Get current date
    today = timezone.now()
    
    context = {
        'user_count': user_count,
        'company_count': company_count,
        'profile_count': profile_count,
        'job_count': job_count,
        'user_growth': user_growth,
        'profile_growth': profile_growth,
        'company_growth': company_growth,
        'job_growth': job_growth,
        'active_users_count': active_users_count,
        'recent_users': recent_users,
        'recent_profiles': recent_profiles,
        'recent_jobs': recent_jobs,
        'recent_access_logs': recent_access_logs,
        'today': today,
    }
    
    return render(request, 'admin/dashboard/index.html', context)

@login_required
def admin_users(request):
    """Admin user management view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get query parameters for filtering
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role_filter', '')
    profile_filter = request.GET.get('profile_filter', '')
    status_filter = request.GET.get('status_filter', '')
    
    # Get all users with filters
    users = User.objects.all().select_related('user_role').order_by('username')
    
    # Apply search filter if provided
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
    
    # Apply role filter if provided
    if role_filter:
        users = users.filter(user_role__role=role_filter)
    
    # Apply profile filter if provided
    if profile_filter == 'with_profile':
        users = users.filter(profile__isnull=False)
    elif profile_filter == 'without_profile':
        users = users.filter(profile__isnull=True)
    
    # Apply status filter if provided
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 9)  # Show 9 users per page
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
    }
    
    return render(request, 'admin/users/index.html', context)

@login_required
def admin_user_create(request):
    """Admin create user view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        role_form = UserRoleForm(request.POST)
        
        if user_form.is_valid() and role_form.is_valid():
            # Create user
            user = user_form.save()
            
            # Set active status if provided
            is_active = request.POST.get('is_active')
            user.is_active = is_active == 'on'
            
            # Set staff status if provided
            is_staff = request.POST.get('is_staff')
            user.is_staff = is_staff == 'on'
            
            user.save()
            
            # Create user role
            user_role = role_form.save(commit=False)
            user_role.user = user
            user_role.save()
            
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('admin_users')
    else:
        user_form = UserRegistrationForm()
        role_form = UserRoleForm()
    
    context = {
        'user_form': user_form,
        'role_form': role_form,
    }
    
    return render(request, 'admin/users/form.html', context)

@login_required
def admin_user_edit(request, user_id):
    """Admin edit user view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the user to edit
    user = get_object_or_404(User, id=user_id)
    
    # Get or create user role
    user_role, created = UserRole.objects.get_or_create(
        user=user,
        defaults={'role': 'user'}
    )
    
    if request.method == 'POST':
        # For editing, we don't use UserRegistrationForm as it includes password fields
        # Instead, we manually handle the fields we want to edit
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        
        # Set active status if provided
        is_active = request.POST.get('is_active')
        user.is_active = is_active == 'on'
        
        # Set staff status if provided
        is_staff = request.POST.get('is_staff')
        user.is_staff = is_staff == 'on'
        
        user.save()
        
        # Update user role
        role_form = UserRoleForm(request.POST, instance=user_role)
        if role_form.is_valid():
            role_form.save()
        
        messages.success(request, f'User {user.username} updated successfully.')
        return redirect('admin_users')
    else:
        # Create a form-like structure for the template
        user_form = user
        role_form = UserRoleForm(instance=user_role)
    
    context = {
        'user_form': user_form,
        'role_form': role_form,
    }
    
    return render(request, 'admin/users/form.html', context)

@login_required
def admin_user_delete(request, user_id):
    """Admin delete user view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the user to delete
    user = get_object_or_404(User, id=user_id)
    
    # Don't allow deleting self
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('admin_users')
    
    # Delete the user
    username = user.username
    user.delete()
    
    messages.success(request, f'User {username} deleted successfully.')
    return redirect('admin_users')

@login_required
def admin_user_password(request, user_id):
    """Admin reset user password view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the user
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 and password2 and password1 == password2:
            user.set_password(password1)
            user.save()
            messages.success(request, f'Password for {user.username} reset successfully.')
            return redirect('admin_users')
        else:
            messages.error(request, 'Passwords do not match.')
    
    context = {
        'user': user,
    }
    
    return render(request, 'admin/users/password.html', context)

@login_required
def role_management(request):
    """Role management view for admins"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    if request.method == 'POST':
        user_id = request.POST.get('user')
        role = request.POST.get('role')
        action = request.POST.get('action')
        
        try:
            user = User.objects.get(id=user_id)
            
            if action == 'delete':
                # Delete user role
                try:
                    user_role = UserRole.objects.get(user=user)
                    user_role.delete()
                    messages.success(request, f'Role for {user.get_full_name() or user.username} has been removed.')
                except UserRole.DoesNotExist:
                    messages.error(request, f'No role found for {user.get_full_name() or user.username}.')
            else:
                # Create or update user role
                user_role, created = UserRole.objects.update_or_create(
                    user=user,
                    defaults={'role': role}
                )
                
                if created:
                    messages.success(request, f'Role assigned to {user.get_full_name() or user.username} successfully.')
                else:
                    messages.success(request, f'Role updated for {user.get_full_name() or user.username} successfully.')
        
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    
    # Get all users and roles for the template
    users = User.objects.all().order_by('username')
    user_roles = UserRole.objects.all().select_related('user').order_by('user__username')
    
    context = {
        'users': users,
        'user_roles': user_roles,
    }
    
    return render(request, 'profile_system/role_management.html', context)

def home(request):
    """Home page view"""
    # Redirect authenticated users to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    job_count = JobPosting.objects.filter(is_active=True).count()
    company_count = Company.objects.count()
    profile_count = Profile.objects.count()
    
    context = {
        'job_count': job_count,
        'company_count': company_count,
        'profile_count': profile_count,
    }
    return render(request, 'profile_system/home.html', context)

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully. Please complete your profile.')
            return redirect('profile_wizard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'profile_system/register.html', {'form': form})

@login_required
def create_profile(request):
    """Create user profile view"""
    try:
        # Check if profile already exists
        profile = request.user.profile
        messages.info(request, 'You already have a profile.')
        return redirect('profile_detail', gsez_id=profile.gsez_id)
    except Profile.DoesNotExist:
        # Get all companies for employment section
        companies = Company.objects.all()
        
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                
                # Update completion status
                profile.update_completion_status('basic_info')
                
                messages.success(request, 'Profile created successfully.')
                
                # If saved as draft, show appropriate message
                if profile.is_draft:
                    messages.info(request, 'Your profile has been saved as a draft. You can complete it later.')
                
                # Redirect to family details with gsez_id parameter
                return redirect('family_details', gsez_id=profile.gsez_id)
            else:
                # Add error message if form is invalid
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ProfileForm(user=request.user)
        
        return render(request, 'profile_system/profile_wizard.html', {'form': form, 'companies': companies})

@login_required
def add_family_details(request, gsez_id):
    """Add family details to a profile"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this profile.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    if request.method == 'POST':
        form = FamilyDetailForm(request.POST)
        if form.is_valid():
            family_detail = form.save(commit=False)
            family_detail.profile = profile
            family_detail.save()
            
            # Update profile completion status
            profile.update_completion_status('family_details')
            
            messages.success(request, 'Family details added successfully.')
            
            # Check if the request is coming from admin panel
            referer = request.META.get('HTTP_REFERER', '')
            if 'custom-admin' in referer:
                return redirect('admin_profiles')
            else:
                return redirect('profile_detail', gsez_id=gsez_id)
    else:
        form = FamilyDetailForm()
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    # Check if the request is coming from admin panel
    referer = request.META.get('HTTP_REFERER', '')
    if 'custom-admin' in referer:
        return render(request, 'admin/users/add_family_details.html', context)
    else:
        return render(request, 'profile_system/add_family_details.html', context)

@login_required
def add_address(request, gsez_id):
    """Add address to a profile"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this profile.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.profile = profile
            address.is_current = True
            address.save()
            
            # Update profile completion status
            profile.update_completion_status('address')
            
            messages.success(request, 'Address added successfully.')
            
            # Check if the request is coming from admin panel
            referer = request.META.get('HTTP_REFERER', '')
            if 'custom-admin' in referer:
                return redirect('admin_profiles')
            else:
                return redirect('profile_detail', gsez_id=gsez_id)
    else:
        form = AddressForm()
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    # Check if the request is coming from admin panel
    referer = request.META.get('HTTP_REFERER', '')
    if 'custom-admin' in referer:
        return render(request, 'admin/users/add_address.html', context)
    else:
        return render(request, 'profile_system/add_address.html', context)

@login_required
def add_permanent_address(request):
    """Add permanent address view"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'Please create your profile first.')
        return redirect('profile_wizard')
    
    if request.method == 'POST':
        form = AddressForm(request.POST, profile=profile)
        if form.is_valid():
            address = form.save(commit=False)
            address.profile = profile
            address.is_current = False
            address.save()
            messages.success(request, 'Permanent address added successfully.')
            return redirect('add_education', gsez_id=profile.gsez_id)
    else:
        form = AddressForm(profile=profile)
        form.initial['is_current'] = False
    
    return render(request, 'profile_system/add_permanent_address.html', {'form': form})

@login_required
def add_education(request, gsez_id):
    """Add education details to a profile"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this profile.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.profile = profile
            education.save()
            
            # Update profile completion status
            profile.update_completion_status('education')
            
            messages.success(request, 'Education details added successfully.')
            
            # Check if the request is coming from admin panel
            referer = request.META.get('HTTP_REFERER', '')
            if 'custom-admin' in referer:
                return redirect('admin_profiles')
            else:
                return redirect('profile_detail', gsez_id=gsez_id)
    else:
        form = EducationForm()
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    # Check if the request is coming from admin panel
    referer = request.META.get('HTTP_REFERER', '')
    if 'custom-admin' in referer:
        return render(request, 'admin/users/add_education.html', context)
    else:
        return render(request, 'profile_system/add_education.html', context)

@login_required
def add_employment(request, gsez_id):
    """Add employment details to a profile"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this profile.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    if request.method == 'POST':
        form = EmploymentForm(request.POST)
        if form.is_valid():
            employment = form.save(commit=False)
            employment.profile = profile
            employment.save()
            
            # Update profile completion status
            profile.update_completion_status('employment')
            
            messages.success(request, 'Employment details added successfully.')
            
            # Check if the request is coming from admin panel
            referer = request.META.get('HTTP_REFERER', '')
            if 'custom-admin' in referer:
                return redirect('admin_profiles')
            else:
                return redirect('profile_detail', gsez_id=gsez_id)
    else:
        form = EmploymentForm()
    
    context = {
        'form': form,
        'profile': profile,
        'companies': Company.objects.all(),
    }
    
    # Check if the request is coming from admin panel
    referer = request.META.get('HTTP_REFERER', '')
    if 'custom-admin' in referer:
        return render(request, 'admin/users/add_employment.html', context)
    else:
        return render(request, 'profile_system/add_employment.html', context)

@login_required
def profile_detail(request, gsez_id):
    """Profile detail view"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if the user is viewing their own profile or is a staff member
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('home')
    
    family_details = profile.family_details.all()
    addresses = profile.addresses.all()
    education = profile.education.all()
    employments = profile.employments.all()
    
    # Calculate profile completion percentage
    completion_percentage = profile.get_completion_percentage()
    
    # Check if user can verify profiles
    can_verify = False
    try:
        user_role = request.user.user_role
        can_verify = user_role.is_admin or user_role.is_hr or request.user.is_staff
    except UserRole.DoesNotExist:
        can_verify = request.user.is_staff
    
    context = {
        'profile': profile,
        'family_details': family_details,
        'addresses': addresses,
        'education': education,
        'employments': employments,
        'completion_percentage': completion_percentage,
        'can_verify': can_verify,
    }
    return render(request, 'profile_system/profile_detail.html', context)

@login_required
def edit_profile(request, gsez_id):
    """Edit profile view"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if the user is editing their own profile or is a staff member
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this profile.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            # Handle the case when photo or govt_id_scan is not provided
            if not form.cleaned_data.get('photo') and 'photo-clear' not in request.POST:
                form.cleaned_data.pop('photo', None)
            if not form.cleaned_data.get('govt_id_scan') and 'govt_id_scan-clear' not in request.POST:
                form.cleaned_data.pop('govt_id_scan', None)
            
            # Save profile
            profile = form.save()
            
            # Update completion status if needed
            if profile.completion_status == 'not_started':
                profile.update_completion_status('basic_info')
            
            messages.success(request, 'Profile updated successfully.')
            
            # Show appropriate message based on draft status
            if profile.is_draft:
                messages.info(request, 'Your profile is still in draft mode. Complete all sections to finalize it.')
                
                # Check if we should continue to next step
                if 'continue_to_next' in request.POST:
                    # Determine next step based on completion status
                    if not profile.family_details.exists():
                        return redirect('family_details', gsez_id=profile.gsez_id)
                    elif not profile.addresses.exists():
                        return redirect('addresses', gsez_id=profile.gsez_id)
                    elif not profile.education.exists():
                        return redirect('education', gsez_id=profile.gsez_id)
                    elif not profile.employments.exists():
                        return redirect('employment', gsez_id=profile.gsez_id)
            
            return redirect('profile_detail', gsez_id=profile.gsez_id)
        else:
            # Add error message if form is invalid
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    
    # Get completion percentage
    completion_percentage = profile.get_completion_percentage()
    
    return render(request, 'profile_system/edit_profile.html', {
        'form': form, 
        'profile': profile,
        'completion_percentage': completion_percentage
    })

@login_required
def dashboard(request):
    """User dashboard view"""
    # Check user role and redirect accordingly
    try:
        user_role = request.user.user_role
        if user_role.is_admin or request.user.is_staff:
            return redirect('admin_dashboard')
    except UserRole.DoesNotExist:
        # If no role is assigned, create default user role
        UserRole.objects.create(user=request.user, role='user')
    
    # Check if user has a profile
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Check if admin has skipped profile creation
        try:
            user_role = request.user.user_role
            if (user_role.is_admin or request.user.is_staff) and user_role.is_skip_profile:
                return redirect('admin_dashboard')
        except UserRole.DoesNotExist:
            pass
            
        messages.info(request, 'Please complete your profile to continue.')
        return redirect('profile_wizard')
    
    # Get user's employment details
    employments = Employment.objects.filter(profile=profile)
    current_employment = employments.filter(is_current=True).first()
    
    # Get job applications
    applications = JobApplication.objects.filter(applicant=profile)
    
    # Get access logs
    access_logs = AccessLog.objects.filter(profile=profile).order_by('-timestamp')[:5]
    
    context = {
        'profile': profile,
        'current_employment': current_employment,
        'applications': applications,
        'access_logs': access_logs,
        'user_type': getattr(request, 'user_type', 'User'),
    }
    return render(request, 'profile_system/dashboard.html', context)

@login_required
def job_list(request):
    """Job listings view"""
    form = JobSearchForm(request.GET)
    jobs = JobPosting.objects.all()
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        location = form.cleaned_data.get('location')
        is_active = form.cleaned_data.get('is_active')
        
        if search_query:
            jobs = jobs.filter(
                Q(title__icontains=search_query) | 
                Q(company__name__icontains=search_query)
            )
        
        if location:
            jobs = jobs.filter(location__icontains=location)
        
        if is_active:
            jobs = jobs.filter(is_active=True)
    
    context = {
        'jobs': jobs,
        'form': form,
    }
    return render(request, 'profile_system/job_list.html', context)

@login_required
def job_detail(request, job_id):
    """Job detail view"""
    job = get_object_or_404(JobPosting, id=job_id)
    
    # Check if user has already applied
    try:
        profile = request.user.profile
        already_applied = JobApplication.objects.filter(job=job, applicant=profile).exists()
    except Profile.DoesNotExist:
        profile = None
        already_applied = False
    
    if request.method == 'POST' and profile:
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = profile
            application.save()
            messages.success(request, 'Application submitted successfully.')
            return redirect('job_list')
    else:
        form = JobApplicationForm()
    
    context = {
        'job': job,
        'form': form,
        'already_applied': already_applied,
    }
    return render(request, 'profile_system/job_detail.html', context)

@login_required
def company_dashboard(request):
    """Company dashboard for HR users"""
    # Check if user is associated with a company
    try:
        company = Company.objects.get(contact_email=request.user.email)
    except Company.DoesNotExist:
        messages.error(request, 'You are not associated with any company.')
        return redirect('home')
    
    job_postings = JobPosting.objects.filter(company=company)
    employees = Employment.objects.filter(company=company, is_current=True)
    
    context = {
        'company': company,
        'job_postings': job_postings,
        'employees': employees,
    }
    return render(request, 'profile_system/company_dashboard.html', context)

@login_required
def create_job_posting(request):
    """Create job posting view"""
    # Check if user is associated with a company
    try:
        company = Company.objects.get(contact_email=request.user.email)
    except Company.DoesNotExist:
        messages.error(request, 'You are not associated with any company.')
        return redirect('home')
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.company = company
            job_posting.save()
            messages.success(request, 'Job posting created successfully.')
            return redirect('company_dashboard')
    else:
        form = JobPostingForm()
    
    return render(request, 'profile_system/create_job_posting.html', {'form': form})

@login_required
def job_applications(request, job_id):
    """View job applications for a specific job posting"""
    job = get_object_or_404(JobPosting, id=job_id)
    
    # Check if user is associated with the company that posted the job
    try:
        company = Company.objects.get(contact_email=request.user.email)
        if job.company != company:
            messages.error(request, 'You do not have permission to view these applications.')
            return redirect('home')
    except Company.DoesNotExist:
        messages.error(request, 'You are not associated with any company.')
        return redirect('home')
    
    applications = JobApplication.objects.filter(job=job)
    
    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'profile_system/job_applications.html', context)

@login_required
def scan_qr(request):
    """QR code scanning view for security personnel"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    if request.method == 'POST':
        gsez_id = request.POST.get('gsez_id')
        try:
            profile = Profile.objects.get(gsez_id=gsez_id)
            return redirect('profile_detail', gsez_id=profile.gsez_id)
        except Profile.DoesNotExist:
            messages.error(request, 'Profile not found.')
    
    return render(request, 'profile_system/scan_qr.html')

@login_required
def log_access(request, gsez_id):
    """Log access entry/exit"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        location = request.POST.get('location')
        
        # Check if profile is allowed access
        if profile.status == 'blocked' or profile.status == 'terminated':
            messages.error(request, f'Access denied. Profile status: {profile.status}')
            return redirect('profile_detail', gsez_id=profile.gsez_id)
        
        # Log the access
        AccessLog.objects.create(
            profile=profile,
            location=location,
            action=action
        )
        
        messages.success(request, f'Access {action} logged successfully.')
        return redirect('profile_detail', gsez_id=profile.gsez_id)
    
    return render(request, 'profile_system/log_access.html', {'profile': profile})

@login_required
def search_profiles(request):
    """Search profiles view for admin and security personnel"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    form = ProfileSearchForm(request.GET)
    profiles = Profile.objects.all()
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        status = form.cleaned_data.get('status')
        nationality = form.cleaned_data.get('nationality')
        
        if search_query:
            profiles = profiles.filter(
                Q(user__first_name__icontains=search_query) | 
                Q(user__last_name__icontains=search_query) |
                Q(gsez_id__icontains=search_query) |
                Q(govt_id_number__icontains=search_query)
            )
        
        if status:
            profiles = profiles.filter(status=status)
        
        if nationality:
            profiles = profiles.filter(nationality__icontains=nationality)
    
    context = {
        'profiles': profiles,
        'form': form,
    }
    return render(request, 'profile_system/search_profiles.html', context)

def debug_urls(request):
    """Debug view to check URL patterns"""
    return render(request, 'profile_system/debug_urls.html')

def custom_login(request):
    """Custom login view with user type verification"""
    if request.user.is_authenticated:
        # Check user role for redirection
        try:
            user_role = request.user.user_role
            if user_role.is_admin or request.user.is_staff:
                return redirect('admin_dashboard')
        except UserRole.DoesNotExist:
            pass
        
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Check user role for redirection
            try:
                user_role = user.user_role
                if user_role.is_admin or user.is_staff:
                    # For admin users, check if they have a profile or have skipped profile creation
                    if user_role.is_skip_profile:
                        # Admin has skipped profile creation
                        return redirect('admin_dashboard')
                    
                    try:
                        profile = user.profile
                        # Admin with profile, go to admin dashboard
                        return redirect('admin_dashboard')
                    except Profile.DoesNotExist:
                        # Admin without profile, give option to create or skip
                        return redirect('profile_wizard')
            except UserRole.DoesNotExist:
                # Create default role if not exists
                UserRole.objects.create(user=user, role='user')
            
            # For non-admin users, profile is required
            try:
                profile = user.profile
                # If profile exists, redirect to dashboard
                return redirect('dashboard')
            except:
                # If no profile, redirect to profile wizard
                messages.info(request, 'Please complete your profile to continue.')
                return redirect('profile_wizard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'profile_system/login.html')

def custom_logout(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
def skip_profile(request):
    """Skip profile creation for admin users"""
    try:
        # Check if user already has a profile
        profile = request.user.profile
        messages.info(request, 'You already have a profile.')
        return redirect('dashboard')
    except Profile.DoesNotExist:
        # Check if user is admin or staff
        if request.user.is_staff:
            # Set is_skip_profile to True for admin users
            user_role, created = UserRole.objects.get_or_create(user=request.user, defaults={'role': 'admin'})
            user_role.is_skip_profile = True
            user_role.save()
            messages.success(request, 'Profile creation skipped successfully.')
            return redirect('admin_dashboard')
        else:
            try:
                user_role = request.user.user_role
                if user_role.is_admin:
                    # Set is_skip_profile to True for admin users
                    user_role.is_skip_profile = True
                    user_role.save()
                    messages.success(request, 'Profile creation skipped successfully.')
                    return redirect('admin_dashboard')
            except UserRole.DoesNotExist:
                pass
        
        # If not admin or staff, redirect to profile wizard
        messages.error(request, 'Only admin users can skip profile creation.')
        return redirect('profile_wizard')

@login_required
def profile_wizard(request):
    """All-in-one profile creation wizard view"""
    try:
        # Check if profile already exists
        profile = request.user.profile
        messages.info(request, 'You already have a profile.')
        return redirect('dashboard')
    except Profile.DoesNotExist:
        # Check if user is admin - profile is optional for admins
        try:
            user_role = request.user.user_role
            if (user_role.is_admin or request.user.is_staff) and user_role.is_skip_profile:
                # Admin has already chosen to skip profile
                return redirect('admin_dashboard')
            elif user_role.is_admin or request.user.is_staff:
                # Show option to skip profile creation
                messages.info(request, 'As an admin, you can skip profile creation if you want.')
        except UserRole.DoesNotExist:
            pass
            
        # Get all companies for employment section
        companies = Company.objects.all()
        
        if request.method == 'POST':
            # Process the form data
            form = ProfileForm(request.POST, request.FILES, user=request.user)
            
            if form.is_valid():
                # Create profile
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                
                # Update completion status
                profile.update_completion_status('basic_info')
                
                # Process family details
                family_names = request.POST.getlist('family_name[]')
                family_relationships = request.POST.getlist('family_relationship[]')
                family_contacts = request.POST.getlist('family_contact[]')
                
                has_family = False
                for i in range(len(family_names)):
                    if family_names[i]:  # Only create if name is provided
                        FamilyDetail.objects.create(
                            profile=profile,
                            name=family_names[i],
                            relationship=family_relationships[i],
                            contact=family_contacts[i]
                        )
                        has_family = True
                
                if has_family:
                    profile.update_completion_status('family_details')
                
                # Process current address
                has_address = False
                if request.POST.get('address_line1'):
                    Address.objects.create(
                        profile=profile,
                        address_line1=request.POST.get('address_line1'),
                        address_line2=request.POST.get('address_line2', ''),
                        city=request.POST.get('city'),
                        state=request.POST.get('state'),
                        country=request.POST.get('country'),
                        postal_code=request.POST.get('postal_code'),
                        is_current=True
                    )
                    has_address = True
                
                # Process permanent address if provided
                if request.POST.get('permanent_address_line1'):
                    Address.objects.create(
                        profile=profile,
                        address_line1=request.POST.get('permanent_address_line1'),
                        address_line2=request.POST.get('permanent_address_line2', ''),
                        city=request.POST.get('permanent_city'),
                        state=request.POST.get('permanent_state'),
                        country=request.POST.get('permanent_country'),
                        postal_code=request.POST.get('permanent_postal_code'),
                        is_current=False
                    )
                    has_address = True
                
                if has_address:
                    profile.update_completion_status('address')
                
                # Process education details
                qualifications = request.POST.getlist('qualification[]')
                institutions = request.POST.getlist('institution[]')
                years = request.POST.getlist('year_of_passing[]')
                
                has_education = False
                for i in range(len(qualifications)):
                    if qualifications[i]:  # Only create if qualification is provided
                        Education.objects.create(
                            profile=profile,
                            qualification=qualifications[i],
                            institution=institutions[i],
                            year_of_passing=years[i]
                        )
                        has_education = True
                
                if has_education:
                    profile.update_completion_status('education')
                
                # Process employment details
                company_id = request.POST.get('company')
                has_employment = False
                if company_id:
                    try:
                        company = Company.objects.get(id=company_id)
                        is_current = request.POST.get('is_current') == 'on'
                        
                        Employment.objects.create(
                            profile=profile,
                            company=company,
                            employee_code=request.POST.get('employee_code'),
                            designation=request.POST.get('designation'),
                            department=request.POST.get('department'),
                            join_date=request.POST.get('join_date'),
                            end_date=request.POST.get('end_date') if not is_current else None,
                            is_current=is_current,
                            remarks=request.POST.get('remarks', '')
                        )
                        has_employment = True
                    except Company.DoesNotExist:
                        messages.warning(request, 'Selected company does not exist. Employment details not saved.')
                
                if has_employment:
                    profile.update_completion_status('employment')
                
                # Check if all sections are completed
                if has_family and has_address and has_education and has_employment:
                    profile.is_draft = False
                    profile.save()
                    messages.success(request, 'Profile created successfully!')
                else:
                    # If not all sections are completed, mark as draft
                    profile.is_draft = True
                    profile.save()
                    messages.success(request, 'Profile created successfully, but it is still in draft mode.')
                    messages.info(request, 'Please complete all sections to finalize your profile.')
                
                return redirect('dashboard')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ProfileForm(user=request.user)
        
        return render(request, 'profile_system/profile_wizard.html', {
            'form': form,
            'companies': companies
        })

@login_required
def admin_profiles(request):
    """Admin profile management view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get query parameters for filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status_filter', '')
    nationality_filter = request.GET.get('nationality_filter', '')
    
    # Get all profiles with filters
    profiles = Profile.objects.all().select_related('user').order_by('-issue_date')
    
    # Apply search filter if provided
    if search_query:
        profiles = profiles.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) | 
            Q(gsez_id__icontains=search_query) |
            Q(nationality__icontains=search_query) |
            Q(govt_id_number__icontains=search_query)
        )
    
    # Apply status filter if provided
    if status_filter:
        profiles = profiles.filter(status=status_filter)
    
    # Apply nationality filter if provided
    if nationality_filter:
        profiles = profiles.filter(nationality=nationality_filter)
    
    # Get distinct nationalities for filter dropdown
    nationalities = Profile.objects.values_list('nationality', flat=True).distinct().order_by('nationality')
    
    # Pagination
    paginator = Paginator(profiles, 10)  # Show 10 profiles per page
    page = request.GET.get('page')
    profiles = paginator.get_page(page)
    
    context = {
        'profiles': profiles,
        'nationalities': nationalities,
    }
    
    return render(request, 'admin/users/profiles.html', context)

@login_required
def admin_profile_create(request):
    """Admin create profile view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get users without profiles
    users_without_profiles = User.objects.filter(profile__isnull=True)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_id = request.POST.get('user')
            try:
                user = User.objects.get(id=user_id)
                
                # Check if user already has a profile
                if hasattr(user, 'profile'):
                    messages.error(request, 'This user already has a profile.')
                    return redirect('admin_profiles')
                
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
                
                messages.success(request, f'Profile created successfully for {user.get_full_name()}.')
                return redirect('admin_profiles')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
    else:
        form = ProfileForm()
    
    context = {
        'form': form,
        'users_without_profiles': users_without_profiles,
    }
    
    return render(request, 'admin/users/profile_create.html', context)

@login_required
def admin_create_profile(request, user_id):
    """Admin create profile for a specific user view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the user
    user = get_object_or_404(User, id=user_id)
    
    # Check if user already has a profile
    if hasattr(user, 'profile'):
        messages.error(request, 'This user already has a profile.')
        return redirect('admin_profiles')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            
            messages.success(request, f'Profile created successfully for {user.get_full_name()}.')
            return redirect('admin_profiles')
    else:
        form = ProfileForm(user=user)
    
    context = {
        'form': form,
        'user': user,
    }
    
    return render(request, 'admin/users/profile_wizard.html', context)

@login_required
def admin_profile_status(request, profile_id, status):
    """Admin change profile status view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the profile
    profile = get_object_or_404(Profile, id=profile_id)
    
    # Validate status
    valid_statuses = ['active', 'blocked', 'terminated', 'surveillance']
    if status not in valid_statuses:
        messages.error(request, 'Invalid status.')
        return redirect('admin_profiles')
    
    # Update status
    profile.status = status
    profile.save()
    
    # Get the display name of the status
    status_display = dict(Profile.STATUS_CHOICES)[status]
    
    messages.success(request, f'Status for {profile.user.get_full_name()} updated to {status_display}.')
    return redirect('admin_profiles')

@login_required
def admin_profile_delete(request, profile_id):
    """Admin delete profile view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the profile
    profile = get_object_or_404(Profile, id=profile_id)
    
    # Delete the profile
    user_name = profile.user.get_full_name()
    profile.delete()
    
    messages.success(request, f'Profile for {user_name} deleted successfully.')
    return redirect('admin_profiles')

@login_required
def admin_companies(request):
    """Admin company management view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get query parameters for filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status_filter', '')
    industry_filter = request.GET.get('industry_filter', '')
    
    # Get all companies with filters
    companies = Company.objects.all().order_by('name')
    
    # Apply search filter if provided
    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) | 
            Q(registration_number__icontains=search_query) | 
            Q(contact_email__icontains=search_query) |
            Q(contact_phone__icontains=search_query) |
            Q(industry__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Apply status filter if provided
    if status_filter:
        companies = companies.filter(status=status_filter)
    
    # Apply industry filter if provided
    if industry_filter:
        companies = companies.filter(industry=industry_filter)
    
    # Enhance companies with additional data
    for company in companies:
        # Count employees
        company.employee_count = Employment.objects.filter(company=company).count()
        
        # Count jobs
        company.job_count = JobPosting.objects.filter(company=company).count()
        
        # Set default rating if not available
        if not hasattr(company, 'rating') or company.rating is None:
            company.rating = 4.0
        
        # Set default review count if not available
        if not hasattr(company, 'review_count') or company.review_count is None:
            company.review_count = 12
    
    # Pagination
    paginator = Paginator(companies, 9)  # Show 9 companies per page
    page = request.GET.get('page')
    companies = paginator.get_page(page)
    
    context = {
        'companies': companies,
    }
    
    return render(request, 'admin/companies/index.html', context)

@login_required
def admin_company_create(request):
    """Admin create company view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    if request.method == 'POST':
        company_form = CompanyForm(request.POST)
        
        if company_form.is_valid():
            company = company_form.save()
            messages.success(request, f'Company {company.name} created successfully.')
            return redirect('admin_companies')
    else:
        company_form = CompanyForm()
    
    context = {
        'company_form': company_form,
    }
    
    return render(request, 'admin/companies/form.html', context)

@login_required
def admin_company_view(request, company_id):
    """Admin view company details"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the company
    company = get_object_or_404(Company, id=company_id)
    
    # Get employees and job postings
    employees = Employment.objects.filter(company=company).select_related('profile__user')
    job_postings = JobPosting.objects.filter(company=company).order_by('-posted_date')
    
    context = {
        'company': company,
        'employees': employees,
        'job_postings': job_postings,
    }
    
    return render(request, 'admin/companies/view.html', context)

@login_required
def admin_company_edit(request, company_id):
    """Admin edit company view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the company
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        company_form = CompanyForm(request.POST, instance=company)
        
        if company_form.is_valid():
            company = company_form.save()
            messages.success(request, f'Company {company.name} updated successfully.')
            return redirect('admin_companies')
    else:
        company_form = CompanyForm(instance=company)
    
    context = {
        'company_form': company_form,
    }
    
    return render(request, 'admin/companies/form.html', context)

@login_required
def admin_company_delete(request, company_id):
    """Admin delete company view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the company
    company = get_object_or_404(Company, id=company_id)
    
    # Check if company has employees
    if Employment.objects.filter(company=company).exists():
        messages.error(request, f'Cannot delete {company.name} because it has employees. Please remove employees first.')
        return redirect('admin_companies')
    
    # Delete the company
    company_name = company.name
    company.delete()
    
    messages.success(request, f'Company {company_name} deleted successfully.')
    return redirect('admin_companies')

@login_required
def admin_company_employees(request, company_id):
    """Admin view company employees"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the company
    company = get_object_or_404(Company, id=company_id)
    
    # Get employees
    employees = Employment.objects.filter(company=company).select_related('profile__user')
    
    context = {
        'company': company,
        'employees': employees,
    }
    
    return render(request, 'admin/companies/employees.html', context)

@login_required
def admin_company_jobs(request, company_id):
    """Admin view company job postings"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the company
    company = get_object_or_404(Company, id=company_id)
    
    # Get job postings
    job_postings = JobPosting.objects.filter(company=company).order_by('-posted_date')
    
    context = {
        'company': company,
        'job_postings': job_postings,
    }
    
    return render(request, 'admin/companies/jobs.html', context)

@login_required
def admin_jobs(request):
    """Admin job management view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get query parameters for filtering
    search_query = request.GET.get('search', '')
    company_filter = request.GET.get('company_filter', '')
    status_filter = request.GET.get('status_filter', '')
    
    # Get all jobs with filters
    jobs = JobPosting.objects.all().select_related('company').order_by('-posted_date')
    
    # Apply search filter if provided
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) | 
            Q(company__name__icontains=search_query) | 
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply company filter if provided
    if company_filter:
        jobs = jobs.filter(company_id=company_filter)
    
    # Apply status filter if provided
    if status_filter == 'active':
        jobs = jobs.filter(is_active=True)
    elif status_filter == 'inactive':
        jobs = jobs.filter(is_active=False)
    
    # Get all companies for filter dropdown
    companies = Company.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'jobs': jobs,
        'companies': companies,
    }
    
    return render(request, 'admin/jobs/index.html', context)

@login_required
def admin_job_create(request):
    """Admin create job view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    if request.method == 'POST':
        job_form = JobPostingForm(request.POST)
        
        if job_form.is_valid():
            job = job_form.save(commit=False)
            
            # Get company
            company_id = request.POST.get('company')
            company = get_object_or_404(Company, id=company_id)
            job.company = company
            
            job.save()
            messages.success(request, f'Job posting "{job.title}" created successfully.')
            return redirect('admin_jobs')
    else:
        job_form = JobPostingForm()
    
    # Get all companies
    companies = Company.objects.all().order_by('name')
    
    context = {
        'job_form': job_form,
        'companies': companies,
    }
    
    return render(request, 'admin/jobs/form.html', context)

@login_required
def admin_job_edit(request, job_id):
    """Admin edit job view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the job
    job = get_object_or_404(JobPosting, id=job_id)
    
    if request.method == 'POST':
        job_form = JobPostingForm(request.POST, instance=job)
        
        if job_form.is_valid():
            job = job_form.save(commit=False)
            
            # Get company
            company_id = request.POST.get('company')
            if company_id and company_id != str(job.company.id):
                company = get_object_or_404(Company, id=company_id)
                job.company = company
            
            job.save()
            messages.success(request, f'Job posting "{job.title}" updated successfully.')
            return redirect('admin_jobs')
    else:
        job_form = JobPostingForm(instance=job)
    
    # Get all companies
    companies = Company.objects.all().order_by('name')
    
    context = {
        'job_form': job_form,
        'job': job,
        'companies': companies,
    }
    
    return render(request, 'admin/jobs/form.html', context)

@login_required
def admin_job_delete(request, job_id):
    """Admin delete job view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the job
    job = get_object_or_404(JobPosting, id=job_id)
    
    # Delete the job
    job_title = job.title
    job.delete()
    
    messages.success(request, f'Job posting "{job_title}" deleted successfully.')
    return redirect('admin_jobs')

@login_required
def admin_job_toggle_status(request, job_id):
    """Admin toggle job status view"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the job
    job = get_object_or_404(JobPosting, id=job_id)
    
    # Toggle status
    job.is_active = not job.is_active
    job.save()
    
    status = "activated" if job.is_active else "deactivated"
    messages.success(request, f'Job posting "{job.title}" {status} successfully.')
    return redirect('admin_jobs')

@login_required
def admin_job_applications(request, job_id):
    """Admin view job applications"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the job
    job = get_object_or_404(JobPosting, id=job_id)
    
    # Get applications
    applications = JobApplication.objects.filter(job=job).select_related('applicant__user').order_by('-application_date')
    
    # Handle status update
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        new_status = request.POST.get('status')
        
        if application_id and new_status:
            application = get_object_or_404(JobApplication, id=application_id)
            application.status = new_status
            application.save()
            messages.success(request, f'Application status updated to {application.get_status_display()}.')
            return redirect('admin_job_applications', job_id=job.id)
    
    context = {
        'job': job,
        'applications': applications,
    }
    
    return render(request, 'admin/jobs/applications.html', context)

@login_required
def admin_user_detail(request, user_id):
    """Admin view user details"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the user
    user = get_object_or_404(User, id=user_id)
    
    # Get user's profile if exists
    try:
        profile = user.profile
        has_profile = True
    except:
        profile = None
        has_profile = False
    
    # Get user's role
    try:
        user_role = user.user_role
    except:
        user_role = None
    
    context = {
        'user': user,
        'profile': profile,
        'has_profile': has_profile,
        'user_role': user_role,
    }
    
    return render(request, 'admin/users/detail.html', context)

@login_required
def admin_user_permissions(request, user_id):
    """Admin manage user permissions"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the user
    user = get_object_or_404(User, id=user_id)
    
    # Get or create user role
    user_role, created = UserRole.objects.get_or_create(user=user, defaults={'role': 'user'})
    
    if request.method == 'POST':
        role_form = UserRoleForm(request.POST, instance=user_role)
        
        if role_form.is_valid():
            role_form.save()
            
            # Update user staff status based on role
            if user_role.role == 'admin':
                user.is_staff = True
                user.save()
            
            messages.success(request, f'Permissions for {user.get_full_name()} updated successfully.')
            return redirect('admin_users')
    else:
        role_form = UserRoleForm(instance=user_role)
    
    context = {
        'user': user,
        'role_form': role_form,
    }
    
    return render(request, 'admin/users/permissions.html', context)

@login_required
def admin_user_toggle_active(request, user_id):
    """Admin toggle user active status"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the user
    user = get_object_or_404(User, id=user_id)
    
    # Toggle active status
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'User {user.get_full_name()} {status} successfully.')
    
    return redirect('admin_users')

@login_required
def admin_company_status(request, company_id, status):
    """Admin change company status"""
    # Check if user is admin or staff
    try:
        user_role = request.user.user_role
        if not user_role.is_admin and not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('home')
    
    # Get the company
    company = get_object_or_404(Company, id=company_id)
    
    # Check if status is valid
    valid_statuses = [choice[0] for choice in Company.STATUS_CHOICES]
    if status not in valid_statuses:
        messages.error(request, f'Invalid status: {status}')
        return redirect('admin_companies')
    
    # Update company status
    company.status = status
    company.save()
    
    status_display = dict(Company.STATUS_CHOICES)[status]
    messages.success(request, f'Company {company.name} status changed to {status_display} successfully.')
    
    return redirect('admin_companies')

@login_required
def verify_profile(request, gsez_id):
    """Profile verification view for admin/HR"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if user has permission to verify profiles
    try:
        user_role = request.user.user_role
        if not (user_role.is_admin or user_role.is_hr or request.user.is_staff):
            messages.error(request, 'You do not have permission to verify profiles.')
            return redirect('home')
    except UserRole.DoesNotExist:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to verify profiles.')
            return redirect('home')
    
    if request.method == 'POST':
        form = ProfileVerificationForm(request.POST)
        if form.is_valid():
            verification_status = form.cleaned_data['verification_status']
            verification_notes = form.cleaned_data['verification_notes']
            
            # Update profile verification status
            profile.verification_status = verification_status
            profile.verification_notes = verification_notes
            
            # If verified, set verified_by and verified_at
            if verification_status == 'verified':
                profile.verified_by = request.user
                profile.verified_at = timezone.now()
            
            profile.save()
            
            messages.success(request, f'Profile verification status updated to {profile.get_verification_status_display()}.')
            
            # Check if the request is coming from admin panel
            referer = request.META.get('HTTP_REFERER', '')
            if 'custom-admin' in referer:
                return redirect('admin_profiles')
            else:
                return redirect('profile_detail', gsez_id=profile.gsez_id)
    else:
        form = ProfileVerificationForm(initial={
            'verification_status': profile.verification_status,
            'verification_notes': profile.verification_notes
        })
    
    # Get profile details for verification
    family_details = profile.family_details.all()
    addresses = profile.addresses.all()
    education = profile.education.all()
    employments = profile.employments.all()
    
    context = {
        'profile': profile,
        'form': form,
        'family_details': family_details,
        'addresses': addresses,
        'education': education,
        'employments': employments,
    }
    
    # Check if the request is coming from admin panel
    referer = request.META.get('HTTP_REFERER', '')
    if 'custom-admin' in referer:
        return render(request, 'admin/users/verify_profile.html', context)
    else:
        return render(request, 'profile_system/verify_profile.html', context)

@login_required
def family_details(request, gsez_id):
    """View family details of a profile"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('home')
    
    family_details = profile.family_details.all()
    
    context = {
        'profile': profile,
        'family_details': family_details,
    }
    
    return render(request, 'profile_system/family_details.html', context)

@login_required
def addresses(request, gsez_id):
    """View addresses of a profile"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('home')
    
    addresses = profile.addresses.all()
    
    context = {
        'profile': profile,
        'addresses': addresses,
    }
    
    return render(request, 'profile_system/addresses.html', context)

@login_required
def education(request, gsez_id):
    """View education details of a profile"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('home')
    
    education = profile.education.all()
    
    context = {
        'profile': profile,
        'education': education,
    }
    
    return render(request, 'profile_system/education.html', context)

@login_required
def employment(request, gsez_id):
    """View employment details of a profile"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('home')
    
    employment = profile.employments.all()
    
    context = {
        'profile': profile,
        'employment': employment,
    }
    
    return render(request, 'profile_system/employment.html', context)

@login_required
def edit_family_detail(request, gsez_id, family_id):
    """Edit a family detail"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    family_detail = get_object_or_404(FamilyDetail, id=family_id, profile=profile)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this profile.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    if request.method == 'POST':
        form = FamilyDetailForm(request.POST, instance=family_detail)
        if form.is_valid():
            form.save()
            messages.success(request, 'Family details updated successfully.')
            return redirect('family_details', gsez_id=gsez_id)
    else:
        form = FamilyDetailForm(instance=family_detail)
    
    context = {
        'form': form,
        'profile': profile,
        'family_detail': family_detail,
        'is_edit': True,
    }
    
    # Check if the request is coming from admin panel
    referer = request.META.get('HTTP_REFERER', '')
    if 'custom-admin' in referer:
        return render(request, 'admin/users/edit_family_details.html', context)
    else:
        return render(request, 'profile_system/edit_family_details.html', context)

@login_required
def delete_family_detail(request, gsez_id, family_id):
    """Delete a family detail"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    family_detail = get_object_or_404(FamilyDetail, id=family_id, profile=profile)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this information.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    family_detail.delete()
    messages.success(request, 'Family detail deleted successfully.')
    
    # Check if there are any family details left
    if not profile.family_details.exists():
        profile.update_completion_status('family_details', False)
    
    return redirect('family_details', gsez_id=gsez_id)

@login_required
def edit_address(request, gsez_id, address_id):
    """Edit an address"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    address = get_object_or_404(Address, id=address_id, profile=profile)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this profile.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('addresses', gsez_id=gsez_id)
    else:
        form = AddressForm(instance=address)
    
    context = {
        'form': form,
        'profile': profile,
        'address': address,
        'is_edit': True,
    }
    
    # Check if the request is coming from admin panel
    referer = request.META.get('HTTP_REFERER', '')
    if 'custom-admin' in referer:
        return render(request, 'admin/users/edit_address.html', context)
    else:
        return render(request, 'profile_system/edit_address.html', context)

@login_required
def delete_address(request, gsez_id, address_id):
    """Delete an address"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    address = get_object_or_404(Address, id=address_id, profile=profile)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this information.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    address.delete()
    messages.success(request, 'Address deleted successfully.')
    
    # Check if there are any addresses left
    if not profile.addresses.exists():
        profile.update_completion_status('addresses', False)
    
    return redirect('addresses', gsez_id=gsez_id)

@login_required
def edit_education(request, gsez_id, education_id):
    """Edit an education entry"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    education = get_object_or_404(Education, id=education_id, profile=profile)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this profile.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Education details updated successfully.')
            return redirect('education', gsez_id=gsez_id)
    else:
        form = EducationForm(instance=education)
    
    context = {
        'form': form,
        'profile': profile,
        'education': education,
        'is_edit': True,
    }
    
    # Check if the request is coming from admin panel
    referer = request.META.get('HTTP_REFERER', '')
    if 'custom-admin' in referer:
        return render(request, 'admin/users/edit_education.html', context)
    else:
        return render(request, 'profile_system/edit_education.html', context)

@login_required
def delete_education(request, gsez_id, education_id):
    """Delete an education entry"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    education = get_object_or_404(Education, id=education_id, profile=profile)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this information.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    education.delete()
    messages.success(request, 'Education entry deleted successfully.')
    
    # Check if there are any education entries left
    if not profile.education.exists():
        profile.update_completion_status('education', False)
    
    return redirect('education', gsez_id=gsez_id)

@login_required
def edit_employment(request, gsez_id, employment_id):
    """Edit an employment entry"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    employment = get_object_or_404(Employment, id=employment_id, profile=profile)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this profile.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    if request.method == 'POST':
        form = EmploymentForm(request.POST, instance=employment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employment details updated successfully.')
            return redirect('employment', gsez_id=gsez_id)
    else:
        form = EmploymentForm(instance=employment)
    
    context = {
        'form': form,
        'profile': profile,
        'employment': employment,
        'is_edit': True,
    }
    
    # Check if the request is coming from admin panel
    referer = request.META.get('HTTP_REFERER', '')
    if 'custom-admin' in referer:
        return render(request, 'admin/users/edit_employment.html', context)
    else:
        return render(request, 'profile_system/edit_employment.html', context)

@login_required
def delete_employment(request, gsez_id, employment_id):
    """Delete an employment entry"""
    profile = get_object_or_404(Profile, gsez_id=gsez_id)
    employment = get_object_or_404(Employment, id=employment_id, profile=profile)
    
    # Check if the user is authorized
    if request.user != profile.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this information.')
        return redirect('profile_detail', gsez_id=gsez_id)
    
    employment.delete()
    messages.success(request, 'Employment entry deleted successfully.')
    
    # Check if there are any employment entries left
    if not profile.employments.exists():
        profile.update_completion_status('employment', False)
    
    return redirect('employment', gsez_id=gsez_id)
