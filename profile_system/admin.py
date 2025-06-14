from django.contrib import admin
from .models import (
    Profile, FamilyDetail, Address, Company, 
    Employment, Education, JobPosting, 
    JobApplication, AccessLog
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('gsez_id', 'get_full_name', 'nationality', 'status')
    list_filter = ('status', 'nationality')
    search_fields = ('gsez_id', 'user__first_name', 'user__last_name', 'govt_id_number')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(FamilyDetail)
class FamilyDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'relationship', 'get_profile_name')
    search_fields = ('name', 'profile__user__first_name', 'profile__user__last_name')
    
    def get_profile_name(self, obj):
        return obj.profile.user.get_full_name()
    get_profile_name.short_description = 'Profile Owner'

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('get_profile_name', 'city', 'country', 'is_current')
    list_filter = ('is_current', 'country')
    
    def get_profile_name(self, obj):
        return obj.profile.user.get_full_name()
    get_profile_name.short_description = 'Profile Owner'

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'contact_email')
    search_fields = ('name', 'registration_number')

@admin.register(Employment)
class EmploymentAdmin(admin.ModelAdmin):
    list_display = ('get_profile_name', 'company', 'designation', 'join_date', 'is_current')
    list_filter = ('is_current', 'company')
    search_fields = ('profile__user__first_name', 'profile__user__last_name', 'company__name')
    
    def get_profile_name(self, obj):
        return obj.profile.user.get_full_name()
    get_profile_name.short_description = 'Employee'

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('get_profile_name', 'qualification', 'institution', 'year_of_passing')
    list_filter = ('year_of_passing',)
    
    def get_profile_name(self, obj):
        return obj.profile.user.get_full_name()
    get_profile_name.short_description = 'Profile Owner'

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'posted_date', 'closing_date', 'is_active')
    list_filter = ('is_active', 'company')
    search_fields = ('title', 'company__name', 'location')

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('get_applicant_name', 'job', 'application_date', 'status')
    list_filter = ('status', 'job__company')
    
    def get_applicant_name(self, obj):
        return obj.applicant.user.get_full_name()
    get_applicant_name.short_description = 'Applicant'

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('get_profile_name', 'timestamp', 'location', 'action')
    list_filter = ('action', 'location')
    
    def get_profile_name(self, obj):
        return obj.profile.user.get_full_name()
    get_profile_name.short_description = 'Profile Owner'
