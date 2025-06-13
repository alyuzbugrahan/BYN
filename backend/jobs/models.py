from django.db import models
from django.conf import settings


class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'job_categories'
        verbose_name_plural = 'Job Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Job(models.Model):
    JOB_TYPES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
        ('volunteer', 'Volunteer'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry level'),
        ('associate', 'Associate'),
        ('mid', 'Mid-Senior level'),
        ('director', 'Director'),
        ('executive', 'Executive'),
    ]
    
    WORKPLACE_TYPES = [
        ('on_site', 'On-site'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    
    # Company and Location
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='jobs')
    location = models.CharField(max_length=200)
    workplace_type = models.CharField(max_length=20, choices=WORKPLACE_TYPES, default='on_site')
    
    # Job Details
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Compensation
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    salary_type = models.CharField(max_length=20, choices=[
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], default='yearly')
    
    # Skills and Tags
    skills_required = models.ManyToManyField('accounts.Skill', related_name='required_for_jobs', blank=True)
    skills_preferred = models.ManyToManyField('accounts.Skill', related_name='preferred_for_jobs', blank=True)
    
    # Status and Metadata
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_jobs')
    application_deadline = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    view_count = models.IntegerField(default=0)
    application_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['location', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min} - {self.salary_max} {self.salary_type}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min}+ {self.salary_type}"
        return "Salary not specified"


class JobApplication(models.Model):
    APPLICATION_STATUS = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('interviewed', 'Interviewed'),
        ('offer_extended', 'Offer Extended'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    
    # Application Content
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    portfolio_url = models.URLField(blank=True)
    
    # Status and Timeline
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='submitted')
    status_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_applications')
    
    # Timestamps
    applied_date = models.DateTimeField(auto_now_add=True)
    status_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'job_applications'
        unique_together = ['job', 'applicant']
        ordering = ['-applied_date']
    
    def __str__(self):
        return f"{self.applicant.full_name} applied for {self.job.title}"


class JobView(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='viewed_jobs', null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'job_views'
        indexes = [
            models.Index(fields=['job', 'viewed_at']),
            models.Index(fields=['user', 'viewed_at']),
        ]
    
    def __str__(self):
        return f"View of {self.job.title} at {self.viewed_at}"


class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by_users')
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_jobs'
        unique_together = ['user', 'job']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.full_name} saved {self.job.title}" 