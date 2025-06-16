from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.utils.translation import gettext_lazy as _
import os
from django.utils import timezone

# Add a property to check if user is in Managers group
User.add_to_class('has_manager_role', property(lambda self: self.groups.filter(name='Managers').exists()))

class UserRole(models.Model):
    """User role model for role-based authentication"""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('hr', 'HR Manager'),
        ('security', 'Security Personnel'),
        ('user', 'Regular User'),
        ('company', 'Company Representative'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_skip_profile = models.BooleanField(default=False, help_text="Whether user has skipped profile creation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_hr(self):
        return self.role == 'hr'
    
    @property
    def is_security(self):
        return self.role == 'security'
    
    @property
    def is_company(self):
        return self.role == 'company'

class Profile(models.Model):
    """Main profile model for GSEZ ID system"""
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gsez_id = models.CharField(max_length=20, unique=True)
    nationality = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    issue_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    govt_id_number = models.CharField(max_length=100)
    govt_id_scan = models.FileField(upload_to='id_scans/', null=True, blank=True)
    emergency_contact = models.CharField(max_length=20)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    
    # Status choices
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('blocked', 'Blocked'),
        ('terminated', 'Terminated'),
        ('surveillance', 'Under Surveillance'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Profile completion tracking
    COMPLETION_CHOICES = [
        ('not_started', 'Not Started'),
        ('basic_info', 'Basic Information Completed'),
        ('family_info', 'Family Information Added'),
        ('address_info', 'Address Information Added'),
        ('education_info', 'Education Information Added'),
        ('employment_info', 'Employment Information Added'),
        ('completed', 'Profile Completed'),
    ]
    completion_status = models.CharField(max_length=20, choices=COMPLETION_CHOICES, default='not_started')
    
    # Verification status
    VERIFICATION_CHOICES = [
        ('unverified', 'Unverified'),
        ('pending', 'Verification Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Verification Rejected'),
    ]
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='unverified')
    verification_notes = models.TextField(blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_profiles')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Profile creation tracking
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_draft = models.BooleanField(default=True, help_text="Whether profile is in draft mode")
    last_step_completed = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.gsez_id}"
    
    def save(self, *args, **kwargs):
        # Generate QR code if not exists
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(f"https://gsez.com/profile/{self.gsez_id}")
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            canvas = Image.new('RGB', (img.pixel_size, img.pixel_size), 'white')
            canvas.paste(img)
            
            buffer = BytesIO()
            canvas.save(buffer, format='PNG')
            self.qr_code.save(f'qr_{self.gsez_id}.png', File(buffer), save=False)
        
        # Update the updated_at field
        self.updated_at = timezone.now()
            
        super().save(*args, **kwargs)
    
    def mark_verified(self, verified_by_user):
        """Mark profile as verified by a specific user"""
        self.verification_status = 'verified'
        self.verified_by = verified_by_user
        self.verified_at = timezone.now()
        self.save()
    
    def mark_verification_rejected(self, notes):
        """Mark profile verification as rejected with notes"""
        self.verification_status = 'rejected'
        self.verification_notes = notes
        self.save()
    
    def update_completion_status(self, step):
        """Update profile completion status based on step completed"""
        step_mapping = {
            'basic_info': 'basic_info',
            'family_details': 'family_info',
            'address': 'address_info',
            'education': 'education_info',
            'employment': 'employment_info',
        }
        
        if step in step_mapping:
            self.completion_status = step_mapping[step]
            self.last_step_completed = step
            
        # Check if all steps are completed
        has_family = self.family_details.exists()
        has_address = self.addresses.exists()
        has_education = self.education.exists()
        has_employment = self.employments.exists()
        
        if has_family and has_address and has_education and has_employment:
            self.completion_status = 'completed'
            self.is_draft = False
        
        self.save()
    
    def get_completion_percentage(self):
        """Calculate profile completion percentage"""
        total_steps = 5  # Basic info, family, address, education, employment
        completed_steps = 0
        
        # Basic info is always considered as first step
        completed_steps += 1
        
        # Check other steps
        if self.family_details.exists():
            completed_steps += 1
        
        if self.addresses.exists():
            completed_steps += 1
            
        if self.education.exists():
            completed_steps += 1
            
        if self.employments.exists():
            completed_steps += 1
            
        return int((completed_steps / total_steps) * 100)

class FamilyDetail(models.Model):
    """Family details of the profile owner"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='family_details')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50)
    contact = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.relationship} of {self.profile.user.get_full_name()}"

class Address(models.Model):
    """Address model for both current and permanent addresses"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='addresses')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_current = models.BooleanField(default=True)
    
    def __str__(self):
        address_type = "Current" if self.is_current else "Permanent"
        return f"{address_type} Address - {self.profile.user.get_full_name()}"

class Company(models.Model):
    """Company model for employers in GSEZ"""
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    address = models.TextField()
    location = models.CharField(max_length=255, default="Gabon Special Economic Zone")
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, default="Manufacturing")
    description = models.TextField(blank=True)
    founded_year = models.IntegerField(default=2000)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='company_covers/', blank=True, null=True)
    
    # Status choices
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('suspended', 'Suspended'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Rating (0-5)
    rating = models.FloatField(default=4.0)
    review_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class Employment(models.Model):
    """Employment record model"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='employments')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    employee_code = models.CharField(max_length=50)
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    join_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    
    # Rating choices
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    
    def __str__(self):
        employment_status = "Current" if self.is_current else "Previous"
        return f"{employment_status} - {self.profile.user.get_full_name()} at {self.company.name}"

class Education(models.Model):
    """Education details model"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    qualification = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    year_of_passing = models.IntegerField()
    
    def __str__(self):
        return f"{self.qualification} - {self.profile.user.get_full_name()}"

class JobPosting(models.Model):
    """Job posting model for job portal"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=100, blank=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"

class JobApplication(models.Model):
    """Job application model"""
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='job_applications')
    application_date = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(blank=True)
    
    # Status choices
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('interviewed', 'Interviewed'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    
    def __str__(self):
        return f"{self.applicant.user.get_full_name()} - {self.job.title}"

class AccessLog(models.Model):
    """Access log for zone entry/exit"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='access_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    action = models.CharField(max_length=10, choices=[('entry', 'Entry'), ('exit', 'Exit')])
    
    def __str__(self):
        return f"{self.profile.user.get_full_name()} - {self.action} at {self.location}"
