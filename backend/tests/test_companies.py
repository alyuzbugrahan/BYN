"""
Simple Company Tests for Available Functionality Only
Tests only the read-only company operations that are actually implemented.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from companies.models import Company, Industry, CompanyFollower

User = get_user_model()


class SimpleCompanyTestCase(APITestCase):
    """Test basic company functionality that exists"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        
        # Create test industry
        self.industry = Industry.objects.create(name='Technology')
        
        # Create test company directly in database (since create view doesn't exist)
        self.company = Company.objects.create(
            name='Tech Innovations Inc',
            description='Leading technology company',
            website='https://techinnovations.com',
            industry=self.industry,
            company_size='51-200',
            founded_year=2010,
            headquarters='San Francisco, CA',
            created_by=self.user
        )
    
    def test_list_companies(self):
        """Test listing companies"""
        response = self.client.get(reverse('company-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_get_company_detail(self):
        """Test retrieving company details"""
        response = self.client.get(reverse('company-detail', kwargs={'id': self.company.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Tech Innovations Inc')
        self.assertEqual(response.data['description'], 'Leading technology company')
    
    def test_follow_company(self):
        """Test following a company"""
        response = self.client.post(reverse('follow-company', kwargs={'company_id': self.company.pk}))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify follow relationship was created
        self.assertTrue(CompanyFollower.objects.filter(user=self.user, company=self.company).exists())
    
    def test_unfollow_company(self):
        """Test unfollowing a company"""
        # First follow the company
        CompanyFollower.objects.create(user=self.user, company=self.company)
        
        response = self.client.delete(reverse('unfollow-company', kwargs={'company_id': self.company.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify follow relationship was removed
        self.assertFalse(CompanyFollower.objects.filter(user=self.user, company=self.company).exists())
    
    def test_followed_companies(self):
        """Test getting followed companies"""
        # Follow the company
        CompanyFollower.objects.create(user=self.user, company=self.company)
        
        response = self.client.get(reverse('followed-companies'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Tech Innovations Inc')
    
    def test_company_stats(self):
        """Test getting company statistics"""
        response = self.client.get(reverse('company-stats', kwargs={'company_id': self.company.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check expected stats fields
        self.assertIn('follower_count', response.data)
        self.assertIn('active_jobs', response.data)
        self.assertIn('total_jobs_posted', response.data)
        self.assertIn('company_size', response.data)
        self.assertEqual(response.data['company_size'], '51-200')
    
    def test_trending_companies(self):
        """Test getting trending companies"""
        response = self.client.get(reverse('trending-companies'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_my_companies(self):
        """Test getting user's administered companies"""
        response = self.client.get(reverse('my-companies'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return empty list since user is not an admin of any company yet
        self.assertIsInstance(response.data, list)
    
    def test_filter_options(self):
        """Test getting filter options"""
        response = self.client.get(reverse('filter-options'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check expected fields
        self.assertIn('industries', response.data)
        self.assertIn('company_sizes', response.data)
        self.assertIn('Technology', response.data['industries'])
    
    def test_company_search_by_name(self):
        """Test searching companies by name"""
        response = self.client.get(reverse('company-list'), {'search': 'Tech'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find our company
        self.assertGreater(len(response.data), 0)
    
    def test_company_filter_by_industry(self):
        """Test filtering companies by industry"""
        response = self.client.get(reverse('company-list'), {'industry': 'Technology'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find our company
        self.assertGreater(len(response.data), 0)
    
    def test_company_filter_by_size(self):
        """Test filtering companies by size"""
        response = self.client.get(reverse('company-list'), {'company_size': '51-200'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find our company
        self.assertGreater(len(response.data), 0) 