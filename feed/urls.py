from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'hashtags', views.HashtagViewSet, basename='hashtag')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'saved-posts', views.SavedPostViewSet, basename='savedpost')
router.register(r'feed-algorithm', views.FeedAlgorithmViewSet, basename='feedalgorithm')
router.register(r'analytics', views.FeedAnalyticsViewSet, basename='analytics')

app_name = 'feed'

urlpatterns = [
    # API routes
    path('', include(router.urls)),
    
    # Additional custom endpoints
    path('posts/<int:post_id>/comments/', views.CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='post-comments'),
] 