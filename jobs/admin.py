from django.contrib import admin
from .models import Job, JobCategory, JobApplication, SavedJob, JobView


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'job_type', 'experience_level', 
                   'is_active', 'is_featured', 'application_count', 'view_count', 'created_at')
    list_filter = ('job_type', 'workplace_type', 'experience_level', 'is_active', 
                  'is_featured', 'company__industry', 'created_at')
    search_fields = ('title', 'description', 'company__name', 'location')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('skills_required', 'skills_preferred')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'requirements', 'responsibilities')
        }),
        ('Company & Location', {
            'fields': ('company', 'location', 'workplace_type')
        }),
        ('Job Details', {
            'fields': ('job_type', 'experience_level', 'category')
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'salary_type')
        }),
        ('Skills', {
            'fields': ('skills_required', 'skills_preferred')
        }),
        ('Status & Meta', {
            'fields': ('is_active', 'is_featured', 'posted_by', 'application_deadline')
        }),
        ('Statistics', {
            'fields': ('view_count', 'application_count'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('view_count', 'application_count')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_date', 'status_updated_at')
    list_filter = ('status', 'applied_date', 'job__company', 'job__job_type')
    search_fields = ('applicant__email', 'applicant__first_name', 'applicant__last_name', 
                    'job__title', 'job__company__name')
    date_hierarchy = 'applied_date'
    
    fieldsets = (
        ('Application Info', {
            'fields': ('job', 'applicant', 'status')
        }),
        ('Application Content', {
            'fields': ('cover_letter', 'resume', 'portfolio_url')
        }),
        ('Status Tracking', {
            'fields': ('status_updated_by', 'applied_date', 'status_updated_at')
        }),
    )
    
    readonly_fields = ('applied_date', 'status_updated_at')


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    list_filter = ('saved_at', 'job__company', 'job__job_type')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'job__title')
    date_hierarchy = 'saved_at'


@admin.register(JobView)
class JobViewAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at', 'job__company')
    search_fields = ('job__title', 'user__email', 'ip_address')
    date_hierarchy = 'viewed_at'
    readonly_fields = ('viewed_at',) 