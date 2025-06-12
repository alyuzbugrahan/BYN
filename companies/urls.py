from django.urls import path
from . import views

urlpatterns = [
    # Company listing and details
    path('companies/', views.CompanyListView.as_view(), name='company-list'),
    path('companies/<int:id>/', views.CompanyDetailView.as_view(), name='company-detail'),
    
    # Company following
    path('companies/<int:company_id>/follow/', views.follow_company, name='follow-company'),
    path('companies/<int:company_id>/unfollow/', views.unfollow_company, name='unfollow-company'),
    path('followed/', views.followed_companies, name='followed-companies'),
    
    # Company statistics and analytics
    path('companies/<int:company_id>/stats/', views.company_stats, name='company-stats'),
    
    # Trending and discovery
    path('trending/', views.trending_companies, name='trending-companies'),
    
    # Admin companies
    path('companies/my-companies/', views.my_companies, name='my-companies'),
    
    # Filter options
    path('filter-options/', views.filter_options, name='filter-options'),
] 