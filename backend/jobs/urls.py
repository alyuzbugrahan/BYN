from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobViewSet,
    JobCategoryViewSet,
    JobApplicationViewSet,
    CompanyJobApplicationsView,
    JobApplicationDetailView,
    SavedJobsView,
    JobStatsView,
)

router = DefaultRouter()
router.register(r'categories', JobCategoryViewSet, basename='job-category')
router.register(r'applications', JobApplicationViewSet, basename='job-application')

urlpatterns = [
    # Specific job endpoints (must come BEFORE router to avoid conflicts)
    path('jobs/my-posts/', JobViewSet.as_view({'get': 'my_posts'}), name='my-job-posts'),
    path('jobs/saved/', JobViewSet.as_view({'get': 'saved'}), name='saved-jobs'),
    path('jobs/recommended/', JobViewSet.as_view({'get': 'recommended'}), name='recommended-jobs'),
    path('jobs/<int:pk>/apply/', JobViewSet.as_view({'post': 'apply'}), name='job-apply'),
    path('jobs/<int:pk>/save/', JobViewSet.as_view({'post': 'save', 'delete': 'save'}), name='job-save'),
    
    # Stats and analytics
    path('stats/', JobStatsView.as_view(), name='job-stats'),
    
    # Application management endpoints
    path('company-applications/', CompanyJobApplicationsView.as_view(), name='company-applications'),
    path('application-detail/<int:pk>/', JobApplicationDetailView.as_view(), name='application-detail'),
    path('applications/<int:pk>/withdraw/', JobApplicationViewSet.as_view({'patch': 'withdraw'}), name='withdraw-application'),
    
    # Router URLs (generic patterns come LAST)
    path('', include(router.urls)),
    
    # Generic jobs endpoints (after specific patterns)
    path('jobs/', JobViewSet.as_view({'get': 'list', 'post': 'create'}), name='job-list'),
    path('jobs/<int:pk>/', JobViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='job-detail'),
] 