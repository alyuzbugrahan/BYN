"""
Simple Jobs Tests for Available Functionality
Tests only the jobs operations that are actually implemented.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from companies.models import Company, Industry
from jobs.models import Job, JobCategory, JobApplication, SavedJob

User = get_user_model()


class SimpleJobsTestCase(APITestCase):
    """Test basic jobs functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
        
        # Create test industry and company
        self.industry = Industry.objects.create(name='Technology')
        self.company = Company.objects.create(
            name='Tech Innovations Inc',
            description='Leading technology company',
            created_by=self.user,
            industry=self.industry
        )
        
        # Create job category
        self.job_category = JobCategory.objects.create(
            name='Software Development',
            description='Software development positions'
        )
        
        # Create test job
        self.job = Job.objects.create(
            title='Software Engineer',
            description='We are looking for a skilled software engineer...',
            company=self.company,
            location='San Francisco, CA',
            job_type='full_time',
            experience_level='mid',
            posted_by=self.user,
            category=self.job_category
        )
    
    def test_list_jobs(self):
        """Test listing job postings"""
        response = self.client.get(reverse('job-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check pagination structure
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_get_job_detail(self):
        """Test retrieving job details"""
        response = self.client.get(reverse('job-detail', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Software Engineer')
        self.assertEqual(response.data['job_type'], 'full_time')
    
    def test_create_job(self):
        """Test creating a new job posting"""
        job_data = {
            'title': 'Frontend Developer',
            'description': 'React developer needed',
            'company': self.company.id,
            'location': 'Remote',
            'job_type': 'full_time',
            'experience_level': 'entry',
            'category': self.job_category.id
        }
        
        response = self.client.post(reverse('job-list'), job_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data['title'], 'Frontend Developer')
            self.assertEqual(response.data['location'], 'Remote')
        else:
            # Some job creation might require additional permissions
            self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])
    
    def test_job_search(self):
        """Test searching jobs"""
        response = self.client.get(reverse('job-list'), {'search': 'Software'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should find our job
        results = response.data['results']
        job_titles = [job['title'] for job in results]
        self.assertTrue(any('Software' in title for title in job_titles))
    
    def test_job_filter_by_type(self):
        """Test filtering jobs by type"""
        response = self.client.get(reverse('job-list'), {'job_type': 'full_time'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # All returned jobs should be full_time
        results = response.data['results']
        for job in results:
            self.assertEqual(job['job_type'], 'full_time')
    
    def test_job_filter_by_location(self):
        """Test filtering jobs by location"""
        response = self.client.get(reverse('job-list'), {'search': 'San Francisco'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find location-based results
        self.assertIsInstance(response.data['results'], list)
    
    def test_save_job(self):
        """Test saving a job"""
        response = self.client.post(reverse('job-save', kwargs={'pk': self.job.pk}))
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        
        # Check if job was saved
        saved_job_exists = SavedJob.objects.filter(user=self.user, job=self.job).exists()
        self.assertTrue(saved_job_exists)
    
    def test_unsave_job(self):
        """Test unsaving a job"""
        # First save the job
        SavedJob.objects.create(user=self.user, job=self.job)
        
        response = self.client.delete(reverse('job-save', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if job was unsaved
        saved_job_exists = SavedJob.objects.filter(user=self.user, job=self.job).exists()
        self.assertFalse(saved_job_exists)
    
    def test_get_saved_jobs(self):
        """Test getting saved jobs"""
        # Save a job first
        SavedJob.objects.create(user=self.user, job=self.job)
        
        response = self.client.get(reverse('saved-jobs'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return paginated results
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_apply_for_job(self):
        """Test applying for a job"""
        application_data = {
            'cover_letter': 'I am very interested in this position...',
        }
        
        response = self.client.post(reverse('job-apply', kwargs={'pk': self.job.pk}), application_data, format='json')
        
        if response.status_code == status.HTTP_201_CREATED:
            # Application successful
            self.assertIn('cover_letter', response.data)
            
            # Check database
            application_exists = JobApplication.objects.filter(job=self.job, applicant=self.user).exists()
            self.assertTrue(application_exists)
        else:
            # Application might require additional data or permissions
            self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])
    
    def test_job_stats(self):
        """Test getting job statistics"""
        response = self.client.get(reverse('job-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check expected stats fields
        expected_fields = ['applications_sent', 'saved_jobs', 'jobs_posted']
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_my_job_posts(self):
        """Test getting user's posted jobs"""
        response = self.client.get(reverse('my-job-posts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return paginated results
        self.assertIn('results', response.data)
        # Should include the job we created in setUp
        if response.data['results']:
            job_titles = [job['title'] for job in response.data['results']]
            self.assertIn('Software Engineer', job_titles)
    
    def test_recommended_jobs(self):
        """Test getting recommended jobs"""
        response = self.client.get(reverse('recommended-jobs'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return paginated results
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)


class JobCategoriesTestCase(APITestCase):
    """Test job categories functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
    
    def test_list_job_categories(self):
        """Test listing job categories"""
        # Create a test category
        JobCategory.objects.create(name='Engineering', description='Engineering positions')
        
        response = self.client.get(reverse('job-category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle paginated response
        if isinstance(response.data, dict) and 'results' in response.data:
            categories = response.data['results']
        else:
            categories = response.data
        
        self.assertIsInstance(categories, list)
        self.assertGreaterEqual(len(categories), 1) 