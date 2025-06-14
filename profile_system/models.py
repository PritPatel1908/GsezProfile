from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.utils.translation import gettext_lazy as _
import os

class Profile(models.Model):
    """Main profile model for GSEZ ID system"""
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gsez_id = models.CharField(max_length=20, unique=True)
    nationality = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    issue_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    photo = models.ImageField(upload_to='profile_photos/')
    govt_id_number = models.CharField(max_length=100)
    govt_id_scan = models.FileField(upload_to='id_scans/')
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
            
        super().save(*args, **kwargs)

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
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    
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
