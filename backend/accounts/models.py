from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level'),
        ('associate', 'Associate'),
        ('mid', 'Mid-Senior Level'),
        ('director', 'Director'),
        ('executive', 'Executive'),
    ]
    
    # Basic fields
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    # Profile fields
    headline = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Professional fields
    current_position = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, blank=True)
    
    # Settings
    is_company_user = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    privacy_public_profile = models.BooleanField(default=True)
    privacy_show_connections = models.BooleanField(default=True)
    
    # System fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def initials(self):
        return f"{self.first_name[0] if self.first_name else ''}{self.last_name[0] if self.last_name else ''}".upper()


class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_experiences'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} at {self.company}"


class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='education')
    school = models.CharField(max_length=100)
    degree = models.CharField(max_length=100, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_education'
        ordering = ['-start_year']
    
    def __str__(self):
        return f"{self.degree} at {self.school}"


class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'skills'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    endorsement_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_skills'
        unique_together = ['user', 'skill']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.skill.name}"


class SkillEndorsement(models.Model):
    user_skill = models.ForeignKey(UserSkill, on_delete=models.CASCADE, related_name='endorsements')
    endorser = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'skill_endorsements'
        unique_together = ['user_skill', 'endorser']
    
    def __str__(self):
        return f"{self.endorser.full_name} endorsed {self.user_skill}" 