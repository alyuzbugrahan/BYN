from django.urls import path
from . import views

urlpatterns = [
    # Company listing and details
    path('companies/', views.CompanyListView.as_view(), name='company-list'),
    path('companies/<int:id>/', views.CompanyDetailView.as_view(), name='company-detail'),
    
    # Company following
    path('companies/<int:company_id>/follow/', views.CompanyFollowView.as_view(), name='follow-company'),
    path('companies/<int:company_id>/unfollow/', views.CompanyUnfollowView.as_view(), name='unfollow-company'),
    path('followed/', views.FollowedCompaniesView.as_view(), name='followed-companies'),
    
    # Company statistics and analytics
    path('companies/<int:company_id>/stats/', views.CompanyStatsView.as_view(), name='company-stats'),
    
    # Trending and discovery
    path('trending/', views.TrendingCompaniesView.as_view(), name='trending-companies'),
    
    # Admin companies
    path('companies/my-companies/', views.MyCompaniesView.as_view(), name='my-companies'),
    
    # Filter options
    path('filter-options/', views.FilterOptionsView.as_view(), name='filter-options'),
] 