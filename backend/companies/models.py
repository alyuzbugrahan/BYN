from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid


class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'industries'
        verbose_name_plural = 'Industries'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Company(models.Model):
    COMPANY_SIZES = [
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1001-5000', '1001-5000 employees'),
        ('5001-10000', '5001-10000 employees'),
        ('10000+', '10000+ employees'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    
    # Profile Information
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZES, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    headquarters = models.CharField(max_length=200, blank=True)
    
    # Media
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='company_covers/', blank=True, null=True)
    
    # Admin and Management
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_companies')
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        through='CompanyAdmin', 
        through_fields=('company', 'user'),
        related_name='administered_companies'
    )
    
    # Metadata
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    follower_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'companies'
        verbose_name_plural = 'Companies'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Company.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class CompanyAdmin(models.Model):
    ADMIN_ROLES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('editor', 'Editor'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ADMIN_ROLES, default='editor')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_company_admins')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'company_admins'
        unique_together = ['company', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.role} at {self.company.name}"


class CompanyFollower(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='followers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_companies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'company_followers'
        unique_together = ['company', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} follows {self.company.name}"


class CompanyLocation(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='locations')
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    is_headquarters = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'company_locations'
    
    def __str__(self):
        return f"{self.company.name} - {self.city}, {self.country}" 