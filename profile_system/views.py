from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import (
    Profile, FamilyDetail, Address, Company, 
    Employment, Education, JobPosting, JobApplication, AccessLog
)
from .forms import (
    UserRegistrationForm, ProfileForm, FamilyDetailForm, 
    AddressForm, CompanyForm, EmploymentForm, EducationForm,
    JobPostingForm, JobApplicationForm, ProfileSearchForm, JobSearchForm
)

def home(request):
    """Home page view"""
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
            return redirect('create_profile')
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
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                messages.success(request, 'Profile created successfully.')
                # Use direct URL to avoid any naming issues
                return redirect('/profile/family-details/')
            else:
                # Add error message if form is invalid
                messages.error(request, 'Please correct the errors below.')
        else:
            form = ProfileForm(user=request.user)
        
        return render(request, 'profile_system/create_profile.html', {'form': form})

@login_required
def add_family_details(request):
    """Add family details view"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'Please create your profile first.')
        return redirect('create_profile')
    
    FamilyDetailFormSet = inlineformset_factory(
        Profile, FamilyDetail, form=FamilyDetailForm, extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        formset = FamilyDetailFormSet(request.POST, instance=profile)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Family details saved successfully.')
            return redirect('add_address')
    else:
        formset = FamilyDetailFormSet(instance=profile)
        # Set user for each form in the formset for pre-filling
        for form in formset.forms:
            form.user = request.user
    
    return render(request, 'profile_system/add_family_details.html', {'formset': formset})

@login_required
def add_address(request):
    """Add address view"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'Please create your profile first.')
        return redirect('create_profile')
    
    if request.method == 'POST':
        form = AddressForm(request.POST, profile=profile)
        if form.is_valid():
            address = form.save(commit=False)
            address.profile = profile
            address.save()
            messages.success(request, 'Address added successfully.')
            
            # Check if permanent address is also needed
            if 'add_permanent' in request.POST:
                return redirect('add_permanent_address')
            else:
                return redirect('add_education')
    else:
        form = AddressForm(profile=profile)
        form.initial['is_current'] = True
    
    return render(request, 'profile_system/add_address.html', {'form': form})

@login_required
def add_permanent_address(request):
    """Add permanent address view"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'Please create your profile first.')
        return redirect('create_profile')
    
    if request.method == 'POST':
        form = AddressForm(request.POST, profile=profile)
        if form.is_valid():
            address = form.save(commit=False)
            address.profile = profile
            address.is_current = False
            address.save()
            messages.success(request, 'Permanent address added successfully.')
            return redirect('add_education')
    else:
        form = AddressForm(profile=profile)
        form.initial['is_current'] = False
    
    return render(request, 'profile_system/add_permanent_address.html', {'form': form})

@login_required
def add_education(request):
    """Add education details view"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'Please create your profile first.')
        return redirect('create_profile')
    
    EducationFormSet = inlineformset_factory(
        Profile, Education, form=EducationForm, extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        formset = EducationFormSet(request.POST, instance=profile)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Education details saved successfully.')
            return redirect('add_employment')
    else:
        formset = EducationFormSet(instance=profile)
        # Set user for each form in the formset for pre-filling
        for form in formset.forms:
            form.user = request.user
    
    return render(request, 'profile_system/add_education.html', {'formset': formset})

@login_required
def add_employment(request):
    """Add employment details view"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'Please create your profile first.')
        return redirect('create_profile')
    
    if request.method == 'POST':
        form = EmploymentForm(request.POST, profile=profile)
        if form.is_valid():
            employment = form.save(commit=False)
            employment.profile = profile
            employment.save()
            messages.success(request, 'Employment details added successfully.')
            return redirect('profile_detail', gsez_id=profile.gsez_id)
    else:
        form = EmploymentForm(profile=profile)
    
    companies = Company.objects.all()
    return render(request, 'profile_system/add_employment.html', {'form': form, 'companies': companies})

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
    
    context = {
        'profile': profile,
        'family_details': family_details,
        'addresses': addresses,
        'education': education,
        'employments': employments,
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
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Handle the case when photo or govt_id_scan is not provided
            if not form.cleaned_data.get('photo'):
                form.cleaned_data.pop('photo', None)
            if not form.cleaned_data.get('govt_id_scan'):
                form.cleaned_data.pop('govt_id_scan', None)
                
            profile = form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile_detail', gsez_id=profile.gsez_id)
        else:
            # Add error message if form is invalid
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'profile_system/edit_profile.html', {'form': form, 'profile': profile})

@login_required
def dashboard(request):
    """User dashboard view"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'Please create your profile first.')
        return redirect('create_profile')
    
    # Get user's job applications
    job_applications = JobApplication.objects.filter(applicant=profile)
    
    # Get current employment
    current_employment = Employment.objects.filter(profile=profile, is_current=True).first()
    
    context = {
        'profile': profile,
        'job_applications': job_applications,
        'current_employment': current_employment,
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
