from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
import json
import qrcode
from io import BytesIO
import csv
from openpyxl import Workbook
from datetime import datetime
from django.core.paginator import Paginator
from PIL import Image
from django.core.files import File
import re

from .models import User, Company, Document, generate_gsezid
from .forms import (
    UserRegistrationForm, UserProfileForm, DocumentForm, 
    CompanyForm, UserManagementForm, CustomAuthenticationForm,
    AdminUserEditForm, AdminUserCreationForm, SimpleUserRegistrationForm
)

# Helper functions for user type checks
def is_admin(user):
    return user.user_type == 'admin'

def is_hr(user):
    return user.user_type == 'hr'

def is_security(user):
    return user.user_type == 'security'

def is_regular_user(user):
    return user.user_type == 'user'

# Authentication views
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'user'  # Default user type
            user.save()
            messages.success(request, f'Account created successfully. Your GSEZ ID is {user.gsezid}. You can now login using this ID.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def simple_register_view(request):
    if request.method == 'POST':
        form = SimpleUserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # First create the user without saving to the database
                user = form.save(commit=False)
                user.user_type = 'user'  # Default user type
                
                # Set default values for all potentially required fields
                user.nationality = 'Not Specified'
                user.current_address = 'Not Provided'
                
                # Use the new GSEZ ID format
                user.gsezid = generate_gsezid()
                
                # Save user
                user.save()
                
                messages.success(request, f'Account created successfully. Your GSEZ ID is {user.gsezid}. You can now login using this ID.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
    else:
        form = SimpleUserRegistrationForm()
    return render(request, 'core/simple_register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            gsezid = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Find the user with the given GSEZID
            try:
                user_obj = User.objects.get(gsezid=gsezid)
                user = authenticate(username=user_obj.username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome, {user.first_name}!')
                    
                    # Redirect based on user type
                    if user.user_type == 'admin':
                        return redirect('admin_dashboard')
                    elif user.user_type == 'hr':
                        return redirect('hr_dashboard')
                    elif user.user_type == 'security':
                        return redirect('security_dashboard')
                    else:
                        return redirect('user_dashboard')
                else:
                    messages.error(request, 'Invalid GSEZ ID or password.')
            except User.DoesNotExist:
                messages.error(request, 'No user found with this GSEZ ID.')
        else:
            messages.error(request, 'Invalid GSEZ ID or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

# User Dashboard
@login_required
@user_passes_test(is_regular_user)
def user_dashboard(request):
    emergency_contacts = {
        'fire': '101',
        'police': '100',
        'ambulance': '108',
        'admin': '+91 9876543210',
        'security': '+91 9876543211'
    }
    return render(request, 'core/user/dashboard.html', {
        'user': request.user,
        'emergency_contacts': emergency_contacts
    })

@login_required
@user_passes_test(is_regular_user)
def user_profile(request):
    documents = Document.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        document_form = DocumentForm(request.POST, request.FILES)
        
        if form.is_valid() and (not document_form.has_changed() or document_form.is_valid()):
            form.save()
            
            if document_form.has_changed() and document_form.is_valid():
                document = document_form.save(commit=False)
                document.user = request.user
                document.save()
                
            messages.success(request, 'Profile updated successfully.')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
        document_form = DocumentForm()
    
    return render(request, 'core/user/profile_card.html', {
        'form': form,
        'document_form': document_form,
        'documents': documents
    })

@login_required
@user_passes_test(is_regular_user)
def user_profile_edit(request):
    # Process JSON fields for display
    emergency_contacts = request.user.get_emergency_contacts()
    family_members = request.user.get_family_members()
    previous_employers = request.user.get_previous_employers() 
    qualifications = request.user.get_qualifications()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        
        # Check for deleted items
        deleted_contacts = request.POST.getlist('deleted_contacts[]', [])
        deleted_family_members = request.POST.getlist('deleted_family_members[]', [])
        deleted_employers = request.POST.getlist('deleted_employers[]', [])
        deleted_qualifications = request.POST.getlist('deleted_qualifications[]', [])
        
        # Process extra items
        contact_names_extra = request.POST.getlist('emergency_contact_name_extra[]', [])
        contact_numbers_extra = request.POST.getlist('emergency_contact_number_extra[]', [])
        
        family_names_extra = request.POST.getlist('family_member_name_extra[]', [])
        family_relations_extra = request.POST.getlist('family_member_relation_extra[]', [])
        family_numbers_extra = request.POST.getlist('family_member_number_extra[]', [])
        
        employer_names_extra = request.POST.getlist('previous_employer_name_extra[]', [])
        employer_join_dates_extra = request.POST.getlist('previous_employer_join_date_extra[]', [])
        employer_leave_dates_extra = request.POST.getlist('previous_employer_leave_date_extra[]', [])
        employer_remarks_extra = request.POST.getlist('previous_employer_remarks_extra[]', [])
        employer_ratings_extra = request.POST.getlist('previous_employer_rating_extra[]', [])
        
        qualification_names_extra = request.POST.getlist('qualification_extra[]', [])
        institution_names_extra = request.POST.getlist('institution_extra[]', [])
        year_of_passings_extra = request.POST.getlist('year_of_passing_extra[]', [])
        
        if form.is_valid():
            user = form.save(commit=False)
            
            # Process emergency contacts
            if deleted_contacts:
                updated_contacts = []
                for i, contact in enumerate(emergency_contacts):
                    if str(i) not in deleted_contacts:
                        updated_contacts.append(contact)
                user.set_emergency_contacts(updated_contacts)
            
            # Add extra emergency contacts
            for i in range(len(contact_names_extra)):
                if contact_names_extra[i] and contact_numbers_extra[i]:
                    emergency_contacts = user.get_emergency_contacts()
                    emergency_contacts.append({
                        'name': contact_names_extra[i],
                        'number': contact_numbers_extra[i]
                    })
                    user.set_emergency_contacts(emergency_contacts)
            
            # Process family members
            if deleted_family_members:
                updated_members = []
                for i, member in enumerate(family_members):
                    if str(i) not in deleted_family_members:
                        updated_members.append(member)
                user.set_family_members(updated_members)
            
            # Process previous employers
            if deleted_employers:
                updated_employers = []
                for i, employer in enumerate(previous_employers):
                    if str(i) not in deleted_employers:
                        updated_employers.append(employer)
                user.set_previous_employers(updated_employers)
            
            # Add extra previous employers
            for i in range(len(employer_names_extra)):
                if employer_names_extra[i]:
                    previous_employers = user.get_previous_employers()
                    previous_employers.append({
                        'company': employer_names_extra[i],
                        'join_date': employer_join_dates_extra[i] if i < len(employer_join_dates_extra) else '',
                        'leave_date': employer_leave_dates_extra[i] if i < len(employer_leave_dates_extra) else '',
                        'remarks': employer_remarks_extra[i] if i < len(employer_remarks_extra) else '',
                        'rating': employer_ratings_extra[i] if i < len(employer_ratings_extra) else ''
                    })
                    user.set_previous_employers(previous_employers)
            
            # Process qualifications
            if deleted_qualifications:
                updated_qualifications = []
                for i, qualification in enumerate(qualifications):
                    if str(i) not in deleted_qualifications:
                        updated_qualifications.append(qualification)
                user.set_qualifications(updated_qualifications)
            
            # Add extra qualifications
            for i in range(len(qualification_names_extra)):
                if qualification_names_extra[i] and institution_names_extra[i]:
                    qualifications = user.get_qualifications()
                    qualifications.append({
                        'qualification': qualification_names_extra[i],
                        'institution': institution_names_extra[i] if i < len(institution_names_extra) else '',
                        'year': year_of_passings_extra[i] if i < len(year_of_passings_extra) else ''
                    })
                    user.set_qualifications(qualifications)
            
            user.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('user_dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/user/profile_edit.html', {
        'form': form,
        'emergency_contacts': emergency_contacts,
        'family_members': family_members,
        'previous_employers': previous_employers,
        'qualifications': qualifications,
    })

@login_required
@user_passes_test(is_regular_user)
def user_profile_card(request):
    return render(request, 'core/user/profile_card.html', {'user': request.user})

@login_required
@user_passes_test(is_regular_user)
def user_job_opportunities(request):
    # In a real application, you would have a Job model
    # For now, let's simulate some job data
    jobs = [
        {
            'id': 1,
            'title': 'Software Developer',
            'company': 'Tech Solutions Ltd',
            'location': 'GSEZ Zone A',
            'description': 'Looking for experienced developers',
            'requirements': 'Python, Django, JavaScript',
            'posted_date': '2023-05-15'
        },
        {
            'id': 2,
            'title': 'Network Administrator',
            'company': 'InfoSec Inc',
            'location': 'GSEZ Zone B',
            'description': 'Managing network infrastructure',
            'requirements': 'CCNA, 3+ years experience',
            'posted_date': '2023-05-20'
        }
    ]
    
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        message = request.POST.get('message')
        
        # In a real application, you would save this to a JobApplication model
        messages.success(request, 'Your job inquiry has been submitted successfully.')
        return redirect('user_job_opportunities')
    
    return render(request, 'core/user/job_opportunities.html', {'jobs': jobs})

@login_required
@user_passes_test(is_regular_user)
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')
            
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')
            
        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, 'Password changed successfully. Please login again.')
        return redirect('login')
        
    return render(request, 'core/user/change_password.html')

# Admin Dashboard
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    users_count = User.objects.filter(user_type='user').count()
    companies_count = Company.objects.count()
    hr_count = User.objects.filter(user_type='hr').count()
    security_count = User.objects.filter(user_type='security').count()
    
    return render(request, 'core/admin/dashboard.html', {
        'users_count': users_count,
        'companies_count': companies_count,
        'hr_count': hr_count,
        'security_count': security_count
    })

@login_required
@user_passes_test(is_admin)
def admin_manage_users(request):
    users = User.objects.filter(user_type='user')
    return render(request, 'core/admin/manage_users.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    documents = Document.objects.filter(user=user)
    
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('admin_user_detail', user_id=user.id)
    else:
        form = UserManagementForm(instance=user)
    
    return render(request, 'core/admin/user_detail.html', {
        'user_obj': user,
        'documents': documents,
        'form': form
    })

@login_required
@user_passes_test(is_admin)
def admin_edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Process additional emergency contacts
            extra_names = request.POST.getlist('emergency_contact_name_extra[]')
            extra_numbers = request.POST.getlist('emergency_contact_number_extra[]')
            
            if extra_names and extra_numbers:
                emergency_contacts = user.get_emergency_contacts()
                for i in range(len(extra_names)):
                    if i < len(extra_numbers) and extra_names[i].strip():
                        emergency_contacts.append({
                            'name': extra_names[i],
                            'number': extra_numbers[i]
                        })
                user.set_emergency_contacts(emergency_contacts)
            
            # Process additional family members
            extra_names = request.POST.getlist('family_member_name_extra[]')
            extra_relations = request.POST.getlist('family_member_relation_extra[]')
            extra_numbers = request.POST.getlist('family_member_number_extra[]')
            
            if extra_names and extra_relations:
                family_members = user.get_family_members()
                for i in range(len(extra_names)):
                    if i < len(extra_relations) and extra_names[i].strip():
                        number = extra_numbers[i] if i < len(extra_numbers) else ''
                        family_members.append({
                            'name': extra_names[i],
                            'relation': extra_relations[i],
                            'number': number
                        })
                user.set_family_members(family_members)
            
            # Process additional previous employers
            extra_companies = request.POST.getlist('previous_employer_name_extra[]')
            extra_join_dates = request.POST.getlist('previous_employer_join_date_extra[]')
            extra_leave_dates = request.POST.getlist('previous_employer_leave_date_extra[]')
            extra_remarks = request.POST.getlist('previous_employer_remarks_extra[]')
            extra_ratings = request.POST.getlist('previous_employer_rating_extra[]')
            
            if extra_companies:
                previous_employers = user.get_previous_employers()
                for i in range(len(extra_companies)):
                    if extra_companies[i].strip():
                        join_date = extra_join_dates[i] if i < len(extra_join_dates) else None
                        leave_date = extra_leave_dates[i] if i < len(extra_leave_dates) else None
                        remarks = extra_remarks[i] if i < len(extra_remarks) else ''
                        rating = extra_ratings[i] if i < len(extra_ratings) and extra_ratings[i].strip() else 0
                        
                        # Convert date objects to strings to make them JSON serializable
                        if join_date:
                            join_date = join_date if isinstance(join_date, str) else join_date.strftime('%Y-%m-%d')
                        if leave_date:
                            leave_date = leave_date if isinstance(leave_date, str) else leave_date.strftime('%Y-%m-%d')
                        
                        previous_employers.append({
                            'company': extra_companies[i],
                            'join_date': join_date,
                            'leave_date': leave_date,
                            'remarks': remarks,
                            'rating': rating
                        })
                user.set_previous_employers(previous_employers)
            
            # Process additional qualifications
            extra_quals = request.POST.getlist('qualification_extra[]')
            extra_insts = request.POST.getlist('institution_extra[]')
            extra_years = request.POST.getlist('year_of_passing_extra[]')
            
            if extra_quals and extra_insts:
                qualifications = user.get_qualifications()
                for i in range(len(extra_quals)):
                    if i < len(extra_insts) and extra_quals[i].strip():
                        year = extra_years[i] if i < len(extra_years) else ''
                        qualifications.append({
                            'qualification': extra_quals[i],
                            'institution': extra_insts[i],
                            'year': year
                        })
                user.set_qualifications(qualifications)
            
            # Save the user with all the additional data
            user.save()
            
            messages.success(request, 'User updated successfully.')
            return redirect('admin_manage_users')
    else:
        form = AdminUserEditForm(instance=user)
    
    # Get existing data for display
    emergency_contacts = user.get_emergency_contacts()
    family_members = user.get_family_members()
    previous_employers = user.get_previous_employers()
    qualifications = user.get_qualifications()
    
    return render(request, 'core/admin/edit_user.html', {
        'user_obj': user,
        'form': form,
        'emergency_contacts': emergency_contacts,
        'family_members': family_members,
        'previous_employers': previous_employers,
        'qualifications': qualifications
    })

@login_required
@user_passes_test(is_admin)
def admin_create_user(request):
    # Generate next GSEZ ID using the new format
    next_gsez_id = generate_gsezid()
    
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # User type is already handled in the form, but we'll leave this line for safety
            user.user_type = request.POST.get('user_type', 'user')
            
            # If no GSEZ ID provided, use the auto-generated one
            if not user.gsezid:
                user.gsezid = next_gsez_id
                
            user.save()
            
            # Process additional emergency contacts
            extra_names = request.POST.getlist('emergency_contact_name_extra[]')
            extra_numbers = request.POST.getlist('emergency_contact_number_extra[]')
            
            if extra_names and extra_numbers:
                emergency_contacts = user.get_emergency_contacts()
                for i in range(len(extra_names)):
                    if i < len(extra_numbers) and extra_names[i].strip():
                        emergency_contacts.append({
                            'name': extra_names[i],
                            'number': extra_numbers[i]
                        })
                user.set_emergency_contacts(emergency_contacts)
            
            # Process additional family members
            extra_names = request.POST.getlist('family_member_name_extra[]')
            extra_relations = request.POST.getlist('family_member_relation_extra[]')
            extra_numbers = request.POST.getlist('family_member_number_extra[]')
            
            if extra_names and extra_relations:
                family_members = user.get_family_members()
                for i in range(len(extra_names)):
                    if i < len(extra_relations) and extra_names[i].strip():
                        number = extra_numbers[i] if i < len(extra_numbers) else ''
                        family_members.append({
                            'name': extra_names[i],
                            'relation': extra_relations[i],
                            'number': number
                        })
                user.set_family_members(family_members)
            
            # Process additional previous employers
            extra_companies = request.POST.getlist('previous_employer_name_extra[]')
            extra_join_dates = request.POST.getlist('previous_employer_join_date_extra[]')
            extra_leave_dates = request.POST.getlist('previous_employer_leave_date_extra[]')
            extra_remarks = request.POST.getlist('previous_employer_remarks_extra[]')
            extra_ratings = request.POST.getlist('previous_employer_rating_extra[]')
            
            if extra_companies:
                previous_employers = user.get_previous_employers()
                for i in range(len(extra_companies)):
                    if extra_companies[i].strip():
                        join_date = extra_join_dates[i] if i < len(extra_join_dates) else None
                        leave_date = extra_leave_dates[i] if i < len(extra_leave_dates) else None
                        remarks = extra_remarks[i] if i < len(extra_remarks) else ''
                        rating = extra_ratings[i] if i < len(extra_ratings) and extra_ratings[i].strip() else 0
                        
                        # Convert date objects to strings to make them JSON serializable
                        if join_date:
                            join_date = join_date if isinstance(join_date, str) else join_date.strftime('%Y-%m-%d')
                        if leave_date:
                            leave_date = leave_date if isinstance(leave_date, str) else leave_date.strftime('%Y-%m-%d')
                        
                        previous_employers.append({
                            'company': extra_companies[i],
                            'join_date': join_date,
                            'leave_date': leave_date,
                            'remarks': remarks,
                            'rating': rating
                        })
                user.set_previous_employers(previous_employers)
            
            # Process additional qualifications
            extra_quals = request.POST.getlist('qualification_extra[]')
            extra_insts = request.POST.getlist('institution_extra[]')
            extra_years = request.POST.getlist('year_of_passing_extra[]')
            
            if extra_quals and extra_insts:
                qualifications = user.get_qualifications()
                for i in range(len(extra_quals)):
                    if i < len(extra_insts) and extra_quals[i].strip():
                        year = extra_years[i] if i < len(extra_years) else ''
                        qualifications.append({
                            'qualification': extra_quals[i],
                            'institution': extra_insts[i],
                            'year': year
                        })
                user.set_qualifications(qualifications)
            
            # Save the user with all the additional data
            user.save()
            
            messages.success(request, 'User created successfully.')
            return redirect('admin_manage_users')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'core/admin/create_user.html', {
        'form': form,
        'next_gsez_id': next_gsez_id
    })

@login_required
@user_passes_test(is_admin)
def admin_manage_companies(request):
    companies = Company.objects.all()
    
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company added successfully.')
            return redirect('admin_manage_companies')
    else:
        form = CompanyForm()
    
    return render(request, 'core/admin/manage_companies.html', {
        'companies': companies,
        'form': form
    })

@login_required
@user_passes_test(is_admin)
def admin_manage_hr(request):
    hrs = User.objects.filter(user_type='hr')
    companies = Company.objects.all()
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'hr'
            user.save()
            
            # Assign company
            company_id = request.POST.get('company')
            if company_id:
                company = Company.objects.get(id=company_id)
                user.current_employer_company = company
                user.save()
                
            messages.success(request, 'HR created successfully.')
            return redirect('admin_manage_hr')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/admin/manage_hr.html', {
        'hrs': hrs,
        'companies': companies,
        'form': form
    })

@login_required
@user_passes_test(is_admin)
def admin_manage_security(request):
    security_staff = User.objects.filter(user_type='security')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'security'
            user.save()
            messages.success(request, 'Security staff created successfully.')
            return redirect('admin_manage_security')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/admin/manage_security.html', {
        'security_staff': security_staff,
        'form': form
    })

@login_required
@user_passes_test(is_admin)
def admin_export_users(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="users.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')
    
    # Sheet header
    row_num = 0
    columns = ['Username', 'First Name', 'Last Name', 'Email', 'GSEZ ID', 'Status', 'User Type']
    
    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title)
    
    # Sheet body
    rows = User.objects.filter(user_type='user').values_list(
        'username', 'first_name', 'last_name', 'email', 'gsezid', 'status', 'user_type'
    )
    
    for row in rows:
        row_num += 1
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, str(cell_value))
    
    wb.save(response)
    return response

@login_required
@user_passes_test(is_admin)
def admin_export_companies(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="companies.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Company Name'])
    
    companies = Company.objects.all().values_list('id', 'company_name')
    for company in companies:
        writer.writerow(company)
    
    return response

@login_required
@user_passes_test(is_admin)
def admin_manage_documents(request):
    documents = Document.objects.all().order_by('-id')
    
    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        documents = documents.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(govt_id_number__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(documents, 10)  # Show 10 documents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/admin/manage_documents.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
@user_passes_test(is_admin)
def admin_create_document(request, user_id=None):
    user = None
    if user_id:
        user = get_object_or_404(User, id=user_id)
    
    # Get all users for dropdown
    users = User.objects.filter(user_type='user')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        selected_user_id = request.POST.get('user')
        
        if not selected_user_id:
            messages.error(request, 'Please select a user for this document.')
            return render(request, 'core/admin/create_document.html', {'form': form, 'users': users, 'selected_user': user})
        
        if form.is_valid():
            document = form.save(commit=False)
            document.user_id = selected_user_id
            document.save()
            messages.success(request, 'Document created successfully.')
            return redirect('admin_manage_documents')
    else:
        form = DocumentForm()
    
    return render(request, 'core/admin/create_document.html', {
        'form': form, 
        'users': users,
        'selected_user': user
    })

@login_required
@user_passes_test(is_admin)
def admin_edit_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, 'Document updated successfully.')
            return redirect('admin_manage_documents')
    else:
        form = DocumentForm(instance=document)
    
    return render(request, 'core/admin/edit_document.html', {
        'form': form,
        'document': document
    })

@login_required
@user_passes_test(is_admin)
def admin_delete_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully.')
        return redirect('admin_manage_documents')
    
    return render(request, 'core/admin/delete_document.html', {
        'document': document
    })

@login_required
def user_documents(request):
    if request.user.user_type == 'admin':
        return redirect('admin_manage_documents')
    
    # For regular users, show only their documents
    documents = Document.objects.filter(user=request.user)
    
    return render(request, 'core/user/documents.html', {
        'documents': documents
    })

# HR Dashboard
@login_required
@user_passes_test(is_hr)
def hr_dashboard(request):
    company = request.user.current_employer_company
    users_in_company = User.objects.filter(current_employer_company=company).count() if company else 0
    
    return render(request, 'core/hr/dashboard.html', {
        'company': company,
        'users_count': users_in_company
    })

@login_required
@user_passes_test(is_hr)
def hr_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('hr_profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/hr/profile.html', {'form': form})

@login_required
@user_passes_test(is_hr)
def hr_manage_company(request):
    company = request.user.current_employer_company
    
    if request.method == 'POST' and company:
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company details updated successfully.')
            return redirect('hr_manage_company')
    else:
        form = CompanyForm(instance=company) if company else None
    
    return render(request, 'core/hr/manage_company.html', {
        'company': company,
        'form': form
    })

@login_required
@user_passes_test(is_hr)
def hr_manage_jobs(request):
    # In a real application, you would have a Job model
    # For now, let's simulate some job data
    jobs = [
        {
            'id': 1,
            'title': 'Software Developer',
            'location': 'GSEZ Zone A',
            'description': 'Looking for experienced developers',
            'requirements': 'Python, Django, JavaScript',
            'posted_date': '2023-05-15'
        },
        {
            'id': 2,
            'title': 'Network Administrator',
            'location': 'GSEZ Zone B',
            'description': 'Managing network infrastructure',
            'requirements': 'CCNA, 3+ years experience',
            'posted_date': '2023-05-20'
        }
    ]
    
    return render(request, 'core/hr/manage_jobs.html', {'jobs': jobs})

@login_required
@user_passes_test(is_hr)
def hr_job_inquiries(request):
    # In a real application, you would have a JobApplication model
    # For now, let's simulate some application data
    applications = [
        {
            'id': 1,
            'job_title': 'Software Developer',
            'applicant_name': 'John Doe',
            'applicant_email': 'john@example.com',
            'message': 'I am interested in this position',
            'status': 'pending',
            'date_applied': '2023-05-16'
        },
        {
            'id': 2,
            'job_title': 'Network Administrator',
            'applicant_name': 'Jane Smith',
            'applicant_email': 'jane@example.com',
            'message': 'I have 5 years of experience',
            'status': 'reviewed',
            'date_applied': '2023-05-21'
        }
    ]
    
    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        status = request.POST.get('status')
        
        # In a real application, you would update the status in the database
        messages.success(request, 'Application status updated successfully.')
        return redirect('hr_job_inquiries')
    
    return render(request, 'core/hr/job_inquiries.html', {'applications': applications})

# Security Dashboard
@login_required
@user_passes_test(is_security)
def security_dashboard(request):
    return render(request, 'core/security/dashboard.html')

@login_required
@user_passes_test(is_security)
def security_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('security_profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/security/profile.html', {'form': form})

@login_required
@user_passes_test(is_security)
def security_add_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'user'
            user.save()
            messages.success(request, 'User added successfully.')
            return redirect('security_dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/security/add_user.html', {'form': form})

@login_required
@user_passes_test(is_security)
def security_scan_qr(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            return render(request, 'core/security/user_details.html', {'user': user})
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('security_scan_qr')
    
    return render(request, 'core/security/scan_qr.html')

# API for company name suggestions
def company_suggestions(request):
    query = request.GET.get('query', '')
    if query:
        companies = Company.objects.filter(company_name__icontains=query).values_list('company_name', flat=True)
        return JsonResponse(list(companies), safe=False)
    return JsonResponse([], safe=False)

def home_view(request):
    """
    Home page view that shows a welcome message and login form if user is not logged in,
    or a welcome back message with links to dashboard if user is logged in.
    """
    if request.user.is_authenticated:
        # User is already logged in, show welcome back message
        return render(request, 'core/index.html')
    else:
        # User is not logged in, show login form
        if request.method == 'POST':
            form = CustomAuthenticationForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Welcome, {user.first_name}!')
                    
                    # Redirect based on user type
                    if user.user_type == 'admin':
                        return redirect('admin_dashboard')
                    elif user.user_type == 'hr':
                        return redirect('hr_dashboard')
                    elif user.user_type == 'security':
                        return redirect('security_dashboard')
                    else:
                        return redirect('user_dashboard')
                else:
                    messages.error(request, 'Invalid username or password.')
        else:
            form = CustomAuthenticationForm()
        
        return render(request, 'core/login.html', {'form': form})
