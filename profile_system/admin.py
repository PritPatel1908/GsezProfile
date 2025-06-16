from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    UserRole, Profile, FamilyDetail, Address, Company, 
    Employment, Education, JobPosting, 
    JobApplication, AccessLog
)

class UserRoleInline(admin.StackedInline):
    model = UserRole
    can_delete = False
    verbose_name_plural = 'User Role'

class UserAdmin(BaseUserAdmin):
    inlines = (UserRoleInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'user_role__role')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    def get_role(self, obj):
        try:
            return obj.user_role.get_role_display()
        except UserRole.DoesNotExist:
            return "No Role"
    get_role.short_description = 'Role'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('gsez_id', 'get_full_name', 'nationality', 'status', 'view_qr_code')
    list_filter = ('status', 'nationality')
    search_fields = ('gsez_id', 'user__first_name', 'user__last_name', 'govt_id_number')
    readonly_fields = ('qr_code_display',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'gsez_id', 'nationality', 'date_of_birth', 'issue_date', 'expiry_date', 'status')
        }),
        ('Identification', {
            'fields': ('photo', 'govt_id_number', 'govt_id_scan', 'emergency_contact')
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_display')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    
    def view_qr_code(self, obj):
        if obj.qr_code:
            return format_html('<a href="{}" target="_blank">View QR Code</a>', obj.qr_code.url)
        return "No QR Code"
    view_qr_code.short_description = 'QR Code'
    
    def qr_code_display(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="200" height="200" />', obj.qr_code.url)
        return "No QR Code"
    qr_code_display.short_description = 'QR Code Preview'

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
    list_display = ('name', 'registration_number', 'contact_email', 'contact_phone')
    search_fields = ('name', 'registration_number')
    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'registration_number', 'address')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'website')
        }),
    )

class EmploymentInline(admin.TabularInline):
    model = Employment
    extra = 0

@admin.register(Employment)
class EmploymentAdmin(admin.ModelAdmin):
    list_display = ('get_profile_name', 'company', 'designation', 'join_date', 'is_current', 'rating')
    list_filter = ('is_current', 'company', 'rating')
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

class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ('application_date',)

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'posted_date', 'closing_date', 'is_active', 'get_applications_count')
    list_filter = ('is_active', 'company')
    search_fields = ('title', 'company__name', 'location')
    inlines = [JobApplicationInline]
    
    def get_applications_count(self, obj):
        count = obj.applications.count()
        url = reverse('admin:profile_system_jobapplication_changelist') + f'?job__id__exact={obj.id}'
        return format_html('<a href="{}">{} applications</a>', url, count)
    get_applications_count.short_description = 'Applications'

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
    list_filter = ('action', 'location', 'timestamp')
    date_hierarchy = 'timestamp'
    
    def get_profile_name(self, obj):
        return obj.profile.user.get_full_name()
    get_profile_name.short_description = 'Profile Owner'

# Custom Admin Site Configuration
admin.site.site_header = 'GSEZ Profile System Administration'
admin.site.site_title = 'GSEZ Admin'
admin.site.index_title = 'GSEZ Profile System Management'
