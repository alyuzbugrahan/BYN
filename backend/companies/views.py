from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Company, Industry, CompanyFollower
from .serializers import (
    CompanySerializer, 
    CompanyDetailSerializer,
    CompanyStatsSerializer,
    FilterOptionsSerializer,
    CompanyFollowSerializer,
    CompanyUnfollowSerializer,
)


class CompanyListView(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]  # Removed DjangoFilterBackend
    search_fields = ['name', 'description', 'industry__name']
    ordering_fields = ['name', 'created_at', 'follower_count']
    ordering = ['-follower_count', 'name']

    def get_queryset(self):
        queryset = Company.objects.select_related('industry', 'created_by').all()
        
        # Filter by industry name if provided
        industry = self.request.query_params.get('industry', None)
        if industry:
            queryset = queryset.filter(industry__name__iexact=industry)
            
        # Filter by company size if provided
        company_size = self.request.query_params.get('company_size', None)
        if company_size:
            queryset = queryset.filter(company_size=company_size)
            
        return queryset


class CompanyDetailView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanyDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'id'


class CompanyFollowView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanyFollowSerializer
    
    def create(self, request, company_id):
        company = get_object_or_404(Company, id=company_id)
        follow, created = CompanyFollower.objects.get_or_create(
            user=request.user,
            company=company
        )
        
        if created:
            company.follower_count += 1
            company.save()
            return Response({'message': 'Company followed successfully'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already following this company'}, status=status.HTTP_200_OK)


class CompanyUnfollowView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanyUnfollowSerializer
    
    def destroy(self, request, company_id):
        company = get_object_or_404(Company, id=company_id)
        try:
            follow = CompanyFollower.objects.get(user=request.user, company=company)
            follow.delete()
            company.follower_count = max(0, company.follower_count - 1)
            company.save()
            return Response({'message': 'Company unfollowed successfully'}, status=status.HTTP_200_OK)
        except CompanyFollower.DoesNotExist:
            return Response({'message': 'Not following this company'}, status=status.HTTP_400_BAD_REQUEST)


class FollowedCompaniesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    
    def get_queryset(self):
        followed = CompanyFollower.objects.filter(user=self.request.user).select_related('company')
        return [follow.company for follow in followed]


class CompanyStatsView(generics.RetrieveAPIView):
    serializer_class = CompanyStatsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self):
        company = get_object_or_404(Company, id=self.kwargs['company_id'])
        from jobs.models import Job
        active_jobs = Job.objects.filter(company=company, is_active=True).count()
        total_jobs = Job.objects.filter(company=company).count()
        
        return {
            'follower_count': company.follower_count,
            'active_jobs': active_jobs,
            'total_jobs_posted': total_jobs,
            'company_size': company.company_size,
            'founded_year': company.founded_year,
        }


class TrendingCompaniesView(generics.ListAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        limit = int(self.request.query_params.get('limit', 10))
        return Company.objects.order_by('-follower_count', '-created_at')[:limit]


class MyCompaniesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer
    
    def get_queryset(self):
        return Company.objects.filter(admins=self.request.user)


class FilterOptionsView(generics.GenericAPIView):
    serializer_class = FilterOptionsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        industries = Industry.objects.values_list('name', flat=True).distinct()
        company_sizes = Company.objects.values_list('company_size', flat=True).distinct().exclude(company_size__isnull=True)
        
        serializer = self.get_serializer({
            'industries': sorted(list(industries)),
            'company_sizes': sorted(list(set(company_sizes)))
        })
        return Response(serializer.data) 