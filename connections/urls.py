from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConnectionRequestViewSet, ConnectionViewSet, FollowViewSet,
    UserRecommendationViewSet, NetworkMetricsViewSet
)

router = DefaultRouter()
router.register(r'requests', ConnectionRequestViewSet, basename='connection-requests')
router.register(r'connections', ConnectionViewSet, basename='connections')
router.register(r'follows', FollowViewSet, basename='follows')
router.register(r'recommendations', UserRecommendationViewSet, basename='user-recommendations')
router.register(r'metrics', NetworkMetricsViewSet, basename='network-metrics')

urlpatterns = [
    path('', include(router.urls)),
] 