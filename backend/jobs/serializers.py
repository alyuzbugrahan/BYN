from rest_framework import serializers
from django.utils.text import slugify
from drf_spectacular.utils import extend_schema_field
from typing import Dict, Optional, Union
from .models import Job, JobCategory, JobApplication, SavedJob
from accounts.serializers import UserBasicSerializer, SkillSerializer
from companies.serializers import CompanyBasicSerializer


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ('id', 'name', 'slug', 'description')
        read_only_fields = ('slug',)
    
    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


class JobListSerializer(serializers.ModelSerializer):
    """Serializer for job listings and search results"""
    company = CompanyBasicSerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    skills_required = SkillSerializer(many=True, read_only=True)
    posted_by = UserBasicSerializer(read_only=True)
    is_saved = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = (
            'id', 'title', 'slug', 'company', 'location', 'workplace_type',
            'job_type', 'experience_level', 'category', 'salary_min', 'salary_max',
            'salary_currency', 'salary_type', 'skills_required', 'is_featured',
            'posted_by', 'application_deadline', 'view_count', 'application_count',
            'created_at', 'is_saved', 'has_applied'
        )
    
    @extend_schema_field(bool)
    def get_is_saved(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedJob.objects.filter(user=request.user, job=obj).exists()
        return False
    
    @extend_schema_field(bool)
    def get_has_applied(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return JobApplication.objects.filter(applicant=request.user, job=obj).exists()
        return False


class JobDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single job view"""
    company = CompanyBasicSerializer(read_only=True)
    category = JobCategorySerializer(read_only=True)
    skills_required = SkillSerializer(many=True, read_only=True)
    skills_preferred = SkillSerializer(many=True, read_only=True)
    posted_by = UserBasicSerializer(read_only=True)
    is_saved = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()
    salary_range = serializers.CharField(read_only=True)
    
    class Meta:
        model = Job
        fields = (
            'id', 'title', 'slug', 'description', 'requirements', 'responsibilities',
            'company', 'location', 'workplace_type', 'job_type', 'experience_level',
            'category', 'salary_min', 'salary_max', 'salary_currency', 'salary_type',
            'salary_range', 'skills_required', 'skills_preferred', 'is_active',
            'is_featured', 'posted_by', 'application_deadline', 'view_count',
            'application_count', 'created_at', 'updated_at', 'is_saved', 'has_applied'
        )
    
    @extend_schema_field(bool)
    def get_is_saved(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedJob.objects.filter(user=request.user, job=obj).exists()
        return False
    
    @extend_schema_field(bool)
    def get_has_applied(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return JobApplication.objects.filter(applicant=request.user, job=obj).exists()
        return False


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating jobs"""
    skills_required_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    skills_preferred_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False
    )
    company_id = serializers.IntegerField(write_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Job
        fields = (
            'title', 'description', 'requirements', 'responsibilities',
            'company_id', 'location', 'workplace_type', 'job_type',
            'experience_level', 'category_id', 'salary_min', 'salary_max',
            'salary_currency', 'salary_type', 'skills_required_names',
            'skills_preferred_names', 'application_deadline'
        )
    
    def create(self, validated_data):
        from accounts.models import Skill
        
        skills_required_names = validated_data.pop('skills_required_names', [])
        skills_preferred_names = validated_data.pop('skills_preferred_names', [])
        company_id = validated_data.pop('company_id')
        category_id = validated_data.pop('category_id', None)
        
        # Set company and category
        from companies.models import Company
        validated_data['company_id'] = company_id
        if category_id:
            validated_data['category_id'] = category_id
        
        # Generate slug
        validated_data['slug'] = slugify(f"{validated_data['title']}-{company_id}")
        
        # Create job
        job = super().create(validated_data)
        
        # Add skills
        if skills_required_names:
            skills_required = []
            for skill_name in skills_required_names:
                skill, created = Skill.objects.get_or_create(name=skill_name)
                skills_required.append(skill)
            job.skills_required.set(skills_required)
        
        if skills_preferred_names:
            skills_preferred = []
            for skill_name in skills_preferred_names:
                skill, created = Skill.objects.get_or_create(name=skill_name)
                skills_preferred.append(skill)
            job.skills_preferred.set(skills_preferred)
        
        return job


class JobApplicationSerializer(serializers.ModelSerializer):
    job = JobListSerializer(read_only=True)
    applicant = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = JobApplication
        fields = (
            'id', 'job', 'applicant', 'cover_letter', 'resume', 'portfolio_url',
            'status', 'applied_date', 'status_updated_at'
        )
        read_only_fields = ('status', 'applied_date', 'status_updated_at')


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = JobApplication
        fields = ('job_id', 'cover_letter', 'resume', 'portfolio_url')
    
    def validate_job_id(self, value):
        try:
            job = Job.objects.get(id=value, is_active=True)
            if JobApplication.objects.filter(
                job=job, 
                applicant=self.context['request'].user
            ).exists():
                raise serializers.ValidationError("You have already applied for this job.")
            return value
        except Job.DoesNotExist:
            raise serializers.ValidationError("Job not found or not active.")
    
    def create(self, validated_data):
        job_id = validated_data.pop('job_id')
        validated_data['job_id'] = job_id
        validated_data['applicant'] = self.context['request'].user
        
        # Increment application count
        job = Job.objects.get(id=job_id)
        job.application_count += 1
        job.save()
        
        return super().create(validated_data)


class JobApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ('status',)
    
    def update(self, instance, validated_data):
        instance.status_updated_by = self.context['request'].user
        return super().update(instance, validated_data)


class SavedJobSerializer(serializers.ModelSerializer):
    job = JobListSerializer(read_only=True)
    
    class Meta:
        model = SavedJob
        fields = ('id', 'job', 'saved_at')
        read_only_fields = ('saved_at',)


class JobBasicSerializer(serializers.ModelSerializer):
    """Lightweight job serializer for use in other serializers"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company_name', 'company_logo',
            'location', 'job_type', 'experience_level'
        ]
    
    @extend_schema_field(str)
    def get_company_logo(self, obj) -> Optional[str]:
        if obj.company and obj.company.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.company.logo.url)
            return obj.company.logo.url
        return None 