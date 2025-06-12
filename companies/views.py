from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Company, Industry, CompanyFollower
from .serializers import CompanySerializer, CompanyDetailSerializer


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_company(request, company_id):
    """Follow a company"""
    company = get_object_or_404(Company, id=company_id)
    
    follow, created = CompanyFollower.objects.get_or_create(
        user=request.user,
        company=company
    )
    
    if created:
        # Update follower count
        company.follower_count += 1
        company.save()
        return Response({'message': 'Company followed successfully'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'message': 'Already following this company'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unfollow_company(request, company_id):
    """Unfollow a company"""
    company = get_object_or_404(Company, id=company_id)
    
    try:
        follow = CompanyFollower.objects.get(user=request.user, company=company)
        follow.delete()
        
        # Update follower count
        company.follower_count = max(0, company.follower_count - 1)
        company.save()
        
        return Response({'message': 'Company unfollowed successfully'}, status=status.HTTP_200_OK)
    except CompanyFollower.DoesNotExist:
        return Response({'message': 'Not following this company'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def followed_companies(request):
    """Get companies followed by the current user"""
    followed = CompanyFollower.objects.filter(user=request.user).select_related('company')
    companies = [follow.company for follow in followed]
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def company_stats(request, company_id):
    """Get company statistics"""
    company = get_object_or_404(Company, id=company_id)
    
    # Get basic stats
    from jobs.models import Job
    active_jobs = Job.objects.filter(company=company, is_active=True).count()
    total_jobs = Job.objects.filter(company=company).count()
    
    stats = {
        'follower_count': company.follower_count,
        'active_jobs': active_jobs,
        'total_jobs_posted': total_jobs,
        'company_size': company.company_size,
        'founded_year': company.founded_year,
    }
    
    return Response(stats)


@api_view(['GET'])
def trending_companies(request):
    """Get trending companies based on recent activity"""
    limit = int(request.query_params.get('limit', 10))
    
    # Companies with most recent job postings and followers
    trending = Company.objects.order_by('-follower_count', '-created_at')[:limit]
    serializer = CompanySerializer(trending, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_companies(request):
    """Get companies where the current user is an admin"""
    companies = Company.objects.filter(admins=request.user)
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def filter_options(request):
    """Get available filter options for industries and company sizes"""
    industries = Industry.objects.values_list('name', flat=True).distinct()
    company_sizes = Company.objects.values_list('company_size', flat=True).distinct().exclude(company_size__isnull=True)
    
    return Response({
        'industries': sorted(list(industries)),
        'company_sizes': sorted(list(set(company_sizes)))  # Remove duplicates and sort
    }) 