from rest_framework import permissions
from .models import Job


class IsJobPosterOrCompanyAdmin(permissions.BasePermission):
    """
    Permission to only allow job posters or company admins to edit/delete jobs
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Instance must have an attribute named `posted_by` or be in a company the user admins
        if hasattr(obj, 'posted_by'):
            # Check if user is the job poster
            if obj.posted_by == request.user:
                return True
            
            # Check if user is an admin of the company that posted the job
            if hasattr(obj, 'company') and obj.company:
                return obj.company.admins.filter(id=request.user.id).exists()
        
        return False


class IsJobApplicationOwner(permissions.BasePermission):
    """
    Permission to only allow applicants to view/edit their own applications
    """
    
    def has_object_permission(self, request, view, obj):
        # Only the applicant can access their own application
        return obj.applicant == request.user


class IsJobPosterOrCompanyAdminForApplication(permissions.BasePermission):
    """
    Permission for job posters/company admins to view and update application status
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is the job poster
        if obj.job.posted_by == request.user:
            return True
        
        # Check if user is an admin of the company that posted the job
        if obj.job.company:
            return obj.job.company.admins.filter(id=request.user.id).exists()
        
        return False


class CanCreateJobForCompany(permissions.BasePermission):
    """
    Permission to create jobs - user must be an admin of the company they're posting for
    """
    
    def has_permission(self, request, view):
        if request.method == 'POST':
            company_id = request.data.get('company_id')
            if company_id:
                from companies.models import Company
                try:
                    company = Company.objects.get(id=company_id)
                    # Check if user is an admin of this company
                    return company.admins.filter(id=request.user.id).exists()
                except Company.DoesNotExist:
                    return False
        
        return True 