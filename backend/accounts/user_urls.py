from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    ExperienceViewSet,
    EducationViewSet,
    UserSkillViewSet,
    UserSearchView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'experiences', ExperienceViewSet, basename='experience')
router.register(r'education', EducationViewSet, basename='education')
router.register(r'skills', UserSkillViewSet, basename='user-skill')

urlpatterns = [
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('profile/<int:pk>/', UserViewSet.as_view({'get': 'retrieve'}), name='user-detail'),
    path('profile/update/', UserViewSet.as_view({'put': 'update', 'patch': 'partial_update'}), name='user-update'),
    path('', include(router.urls)),
] 