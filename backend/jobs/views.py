from django.shortcuts import render
from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, F, Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Job, JobCategory, JobApplication, SavedJob, JobView
from .serializers import (
    JobListSerializer,
    JobDetailSerializer,
    JobCreateUpdateSerializer,
    JobCategorySerializer,
    JobApplicationSerializer,
    JobApplicationCreateSerializer,
    JobApplicationStatusUpdateSerializer,
    SavedJobSerializer,
)
from .filters import JobFilter
from .permissions import IsJobPosterOrCompanyAdmin


class JobPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ['title', 'description', 'company__name', 'location']
    ordering_fields = ['created_at', 'application_deadline', 'salary_min', 'view_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JobDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return JobCreateUpdateSerializer
        return JobListSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsJobPosterOrCompanyAdmin()]
        return [IsAuthenticatedOrReadOnly()]
    
    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track job view
        if request.user.is_authenticated:
            job_view, created = JobView.objects.get_or_create(
                job=instance,
                user=request.user,
                defaults={
                    'ip_address': self.get_client_ip(request),
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')
                }
            )
        else:
            JobView.objects.create(
                job=instance,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        # Increment view count
        Job.objects.filter(id=instance.id).update(view_count=F('view_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def apply(self, request, pk=None):
        """Apply for a job"""
        job = self.get_object()
        
        # Check if user already applied
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            return Response(
                {'error': 'You have already applied for this job.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = JobApplicationCreateSerializer(
            data={**request.data, 'job_id': job.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        
        return Response(
            JobApplicationSerializer(application).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def save(self, request, pk=None):
        """Save or unsave a job"""
        job = self.get_object()
        
        if request.method == 'POST':
            saved_job, created = SavedJob.objects.get_or_create(
                user=request.user,
                job=job
            )
            if created:
                return Response({'message': 'Job saved successfully'})
            return Response({'message': 'Job already saved'})
        
        elif request.method == 'DELETE':
            try:
                saved_job = SavedJob.objects.get(user=request.user, job=job)
                saved_job.delete()
                return Response({'message': 'Job unsaved successfully'})
            except SavedJob.DoesNotExist:
                return Response(
                    {'error': 'Job not in saved list'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        """Get jobs posted by current user or jobs from companies they admin"""
        jobs = self.queryset.filter(
            Q(posted_by=request.user) |
            Q(company__admins=request.user)
        ).distinct()
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def saved(self, request):
        """Get saved jobs"""
        saved_jobs = SavedJob.objects.filter(user=request.user).select_related('job')
        page = self.paginate_queryset([saved_job.job for saved_job in saved_jobs])
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer([saved_job.job for saved_job in saved_jobs], many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def recommended(self, request):
        """Get recommended jobs based on user profile"""
        user = request.user
        
        # Get jobs matching user's skills
        user_skills = user.user_skills.values_list('skill_id', flat=True)
        recommended_jobs = self.queryset.filter(
            Q(skills_required__in=user_skills) | Q(skills_preferred__in=user_skills)
        ).distinct()
        
        # Filter by experience level if available
        if user.experience_level:
            recommended_jobs = recommended_jobs.filter(experience_level=user.experience_level)
        
        # Filter by industry if available
        if user.industry:
            recommended_jobs = recommended_jobs.filter(company__industry__name__icontains=user.industry)
        
        # Exclude already applied jobs
        applied_job_ids = JobApplication.objects.filter(
            applicant=user
        ).values_list('job_id', flat=True)
        recommended_jobs = recommended_jobs.exclude(id__in=applied_job_ids)
        
        page = self.paginate_queryset(recommended_jobs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(recommended_jobs, many=True)
        return Response(serializer.data)


class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]


@extend_schema_view(
    list=extend_schema(description='List job applications'),
    retrieve=extend_schema(description='Get a specific job application'),
    create=extend_schema(description='Create a job application'),
    update=extend_schema(description='Update a job application'),
    withdraw=extend_schema(description='Withdraw a job application')
)
class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    queryset = JobApplication.objects.none()  # Default empty queryset
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return JobApplication.objects.none()
        return JobApplication.objects.filter(applicant=self.request.user)


@extend_schema_view(
    list=extend_schema(description='List job applications for company jobs')
)
class CompanyJobApplicationsView(generics.ListAPIView):
    """View for company admins to see applications for their jobs"""
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'job']
    ordering_fields = ['applied_date', 'status']
    ordering = ['-applied_date']
    queryset = JobApplication.objects.none()  # Default empty queryset
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return JobApplication.objects.none()
        # Get jobs posted by current user or jobs from companies they admin
        return JobApplication.objects.filter(
            Q(job__posted_by=self.request.user) |
            Q(job__company__admins=self.request.user)
        ).select_related('job', 'applicant')


class JobApplicationDetailView(generics.RetrieveUpdateAPIView):
    """View for updating job application status (for employers)"""
    serializer_class = JobApplicationStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only allow access to applications for jobs the user posted or company they admin
        user_jobs = Job.objects.filter(
            Q(posted_by=self.request.user) |
            Q(company__admins=self.request.user)
        )
        
        return JobApplication.objects.filter(job__in=user_jobs)


class SavedJobsView(generics.ListAPIView):
    """List saved jobs for authenticated user"""
    serializer_class = SavedJobSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = JobPagination
    
    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related('job')


class JobStatsView(generics.RetrieveAPIView):
    """Get job statistics for dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Get user's job-related statistics
        stats = {
            'applications_sent': JobApplication.objects.filter(applicant=user).count(),
            'applications_pending': JobApplication.objects.filter(
                applicant=user, status='submitted'
            ).count(),
            'applications_under_review': JobApplication.objects.filter(
                applicant=user, status='under_review'
            ).count(),
            'saved_jobs': SavedJob.objects.filter(user=user).count(),
            'jobs_posted': Job.objects.filter(posted_by=user).count(),
            'active_jobs_posted': Job.objects.filter(posted_by=user, is_active=True).count(),
        }
        
        # If user has posted jobs, get application stats
        if stats['jobs_posted'] > 0:
            user_jobs = Job.objects.filter(posted_by=user)
            stats.update({
                'total_applications_received': JobApplication.objects.filter(
                    job__in=user_jobs
                ).count(),
                'new_applications': JobApplication.objects.filter(
                    job__in=user_jobs, status='submitted'
                ).count(),
            })
        
        return Response(stats) 