from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        
        # Skip authentication check for public URLs
        public_urls = [
            reverse('login'),
            reverse('register'),
            reverse('home'),
            '/admin/login/',
            '/admin/',
        ]
        
        if request.path in public_urls or request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            if not request.path.startswith('/admin/'):
                messages.error(request, 'Please login to access this page.')
                return redirect('login')
            return self.get_response(request)
        
        # Admin URLs are handled by Django's admin authentication
        if request.path.startswith('/admin/'):
            return self.get_response(request)
        
        # Check role-based access
        try:
            user_role = request.user.user_role
            
            # Admin role has access to everything
            if user_role.is_admin or request.user.is_staff:
                request.user_type = 'Admin'
                # Skip profile check for admins
                request.admin_user = True
                return self.get_response(request)
            
            # HR role access
            if user_role.is_hr:
                request.user_type = 'HR'
                hr_urls = [
                    reverse('company_dashboard'),
                    reverse('create_job_posting'),
                    reverse('job_list'),
                    '/company/',
                    '/jobs/',
                ]
                
                if any(request.path.startswith(url) for url in hr_urls):
                    return self.get_response(request)
            
            # Security role access
            if user_role.is_security:
                request.user_type = 'Gate'
                security_urls = [
                    reverse('scan_qr'),
                    reverse('search_profiles'),
                    '/profile/',
                ]
                
                if any(request.path.startswith(url) for url in security_urls):
                    return self.get_response(request)
            
            # Company role access
            if user_role.is_company:
                request.user_type = 'Company'
                company_urls = [
                    reverse('company_dashboard'),
                    '/company/',
                    '/jobs/',
                ]
                
                if any(request.path.startswith(url) for url in company_urls):
                    return self.get_response(request)
            
            # Regular user access (default)
            request.user_type = 'User'
            
        except Exception:
            # If user doesn't have a role, treat as regular user
            request.user_type = 'User'
        
        response = self.get_response(request)
        return response 