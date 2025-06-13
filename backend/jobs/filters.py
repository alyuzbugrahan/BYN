import django_filters
from django.db import models
from .models import Job, JobCategory


class JobFilter(django_filters.FilterSet):
    # Location filters
    location = django_filters.CharFilter(lookup_expr='icontains')
    
    # Company filters
    company_name = django_filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    company_id = django_filters.NumberFilter(field_name='company__id')
    
    # Job type filters
    job_type = django_filters.MultipleChoiceFilter(choices=Job.JOB_TYPES)
    workplace_type = django_filters.MultipleChoiceFilter(choices=Job.WORKPLACE_TYPES)
    experience_level = django_filters.MultipleChoiceFilter(choices=Job.EXPERIENCE_LEVELS)
    
    # Category filter
    category = django_filters.ModelChoiceFilter(queryset=JobCategory.objects.all())
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    
    # Salary filters
    salary_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    salary_range_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_range_max = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    
    # Skills filter
    skills = django_filters.CharFilter(method='filter_skills')
    
    # Date filters
    posted_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    posted_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Application deadline filter
    deadline_after = django_filters.DateFilter(field_name='application_deadline', lookup_expr='gte')
    deadline_before = django_filters.DateFilter(field_name='application_deadline', lookup_expr='lte')
    
    # Featured jobs
    is_featured = django_filters.BooleanFilter()
    
    # Industry filter (through company)
    industry = django_filters.CharFilter(field_name='company__industry__name', lookup_expr='icontains')
    
    class Meta:
        model = Job
        fields = {
            'title': ['icontains'],
            'description': ['icontains'],
            'is_active': ['exact'],
        }
    
    def filter_skills(self, queryset, name, value):
        """Filter jobs by skills (both required and preferred)"""
        skill_names = [skill.strip() for skill in value.split(',') if skill.strip()]
        if skill_names:
            return queryset.filter(
                models.Q(skills_required__name__in=skill_names) |
                models.Q(skills_preferred__name__in=skill_names)
            ).distinct()
        return queryset 