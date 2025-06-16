from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Profile, FamilyDetail, Address, Company, 
    Employment, Education, JobPosting, JobApplication, UserRole
)

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserRole
        fields = ('role',)
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

class ProfileForm(forms.ModelForm):
    save_as_draft = forms.BooleanField(
        required=False, 
        initial=True,
        label='Save as draft',
        help_text='You can complete your profile later if you save it as draft.'
    )
    
    class Meta:
        model = Profile
        exclude = ('user', 'qr_code', 'issue_date', 'completion_status', 'verification_status', 
                  'verification_notes', 'verified_by', 'verified_at', 'created_at', 'updated_at',
                  'last_step_completed')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gsez_id': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'govt_id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_draft': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        # Make photo and govt_id_scan not required when editing
        if instance:
            self.fields['photo'].required = False
            self.fields['govt_id_scan'].required = False
            self.fields['save_as_draft'].initial = instance.is_draft
        else:
            # Make photo and govt_id_scan not required for new profiles
            self.fields['photo'].required = False
            self.fields['govt_id_scan'].required = False
            
        # Pre-fill fields from user data if available
        if user and not instance:
            # Generate a GSEZ ID based on user data (customize as needed)
            self.initial['gsez_id'] = f"GSEZ-{user.id:05d}"
            # Pre-fill emergency contact with user's email if no other data available
            self.initial['emergency_contact'] = user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Handle is_draft based on save_as_draft field
        profile.is_draft = self.cleaned_data.get('save_as_draft', True)
        
        # Update completion status to basic_info
        if not profile.completion_status or profile.completion_status == 'not_started':
            profile.completion_status = 'basic_info'
            profile.last_step_completed = 'basic_info'
        
        if commit:
            profile.save()
        
        return profile

class FamilyDetailForm(forms.ModelForm):
    class Meta:
        model = FamilyDetail
        exclude = ('profile',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill with user data if available and this is a new form
        if user and not self.instance.pk:
            # You can add pre-filling logic here if needed
            pass

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('profile',)
        widgets = {
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill with profile data if available
        if profile and not self.instance.pk:
            # Pre-fill country with nationality from profile
            self.initial['country'] = profile.nationality

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

class EmploymentForm(forms.ModelForm):
    class Meta:
        model = Employment
        exclude = ('profile',)
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'employee_code': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill with profile data if available
        if profile and not self.instance.pk:
            # Set is_current to True by default
            self.initial['is_current'] = True
            # You can add more pre-filling logic here if needed

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ('profile',)
        widgets = {
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_passing': forms.NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2100'}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill with user data if available and this is a new form
        if user and not self.instance.pk:
            # You can add pre-filling logic here if needed
            pass

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        exclude = ('company', 'posted_date')
        widgets = {
            'closing_date': forms.DateInput(attrs={'type': 'date'}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ('cover_letter',)

class ProfileSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False, 
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search by Name, GSEZ ID, or Govt ID'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', '-- All Statuses --')] + list(Profile.STATUS_CHOICES)
    )
    nationality = forms.CharField(required=False, label='Nationality')

class JobSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False, 
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search by Job Title or Company'})
    )
    location = forms.CharField(required=False, label='Location')
    is_active = forms.BooleanField(required=False, label='Active Jobs Only', initial=True)

class ProfileVerificationForm(forms.Form):
    verification_status = forms.ChoiceField(
        choices=Profile.VERIFICATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    verification_notes = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    ) 