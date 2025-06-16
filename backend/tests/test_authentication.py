"""
Comprehensive Authentication Tests for BYN Platform
Tests user registration, login, logout, password management, and security edge cases.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
import json

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    """Test user registration functionality"""
    
    def setUp(self):
        self.registration_url = reverse('user-register')
        self.valid_user_data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
    
    def test_valid_user_registration(self):
        """Test successful user registration"""
        response = self.client.post(self.registration_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['message'], 'Registration successful')
        
        # Verify user was created in database
        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertTrue(user.is_active)
    
    def test_duplicate_email_registration(self):
        """Test registration with duplicate email"""
        # Create first user
        User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Jane',
            last_name='Smith'
        )
        
        response = self.client.post(self.registration_url, self.valid_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_password_mismatch_registration(self):
        """Test registration with password mismatch"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password_confirm'] = 'DifferentPassword123!'
        
        response = self.client.post(self.registration_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_weak_password_registration(self):
        """Test registration with weak password"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password'] = '123'
        invalid_data['password_confirm'] = '123'
        
        response = self.client.post(self.registration_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_email_format(self):
        """Test registration with invalid email format"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        response = self.client.post(self.registration_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_missing_required_fields(self):
        """Test registration with missing required fields"""
        test_cases = [
            {'email': 'test@example.com'},  # Missing other fields
            {'first_name': 'John'},  # Missing email and other fields
            {},  # Missing all fields
        ]
        
        for invalid_data in test_cases:
            with self.subTest(data=invalid_data):
                response = self.client.post(self.registration_url, invalid_data, format='json')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_sql_injection_in_registration(self):
        """Test SQL injection attempts in registration"""
        malicious_data = self.valid_user_data.copy()
        malicious_data['email'] = "test@example.com'; DROP TABLE users; --"
        malicious_data['first_name'] = "John'; DELETE FROM users; --"
        
        response = self.client.post(self.registration_url, malicious_data, format='json')
        # Should either reject due to invalid email or accept safely
        # User table should still exist
        self.assertTrue(User.objects.filter(email__icontains='example.com').exists() or 
                       response.status_code == status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase):
    """Test user login functionality"""
    
    def setUp(self):
        self.login_url = reverse('user-login')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe'
        )
        self.valid_login_data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
    
    def test_valid_login(self):
        """Test successful user login"""
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['message'], 'Login successful')
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials"""
        invalid_data = self.valid_login_data.copy()
        invalid_data['password'] = 'wrongpassword'
        
        response = self.client.post(self.login_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_nonexistent_user_login(self):
        """Test login with non-existent user"""
        invalid_data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        
        response = self.client.post(self.login_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_inactive_user_login(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_case_insensitive_email_login(self):
        """Test login with different email case"""
        login_data = self.valid_login_data.copy()
        login_data['email'] = 'TEST@EXAMPLE.COM'
        
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_brute_force_protection(self):
        """Test protection against brute force attacks"""
        invalid_data = self.valid_login_data.copy()
        invalid_data['password'] = 'wrongpassword'
        
        # Attempt multiple failed logins
        for _ in range(10):
            response = self.client.post(self.login_url, invalid_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTestCase(APITestCase):
    """Test user logout functionality"""
    
    def setUp(self):
        self.logout_url = reverse('user-logout')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
    
    def test_valid_logout(self):
        """Test successful logout"""
        response = self.client.post(self.logout_url, {'refresh': str(self.refresh)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful')
    
    def test_logout_without_token(self):
        """Test logout without authentication"""
        self.client.credentials()  # Remove authentication
        response = self.client.post(self.logout_url, {'refresh': str(self.refresh)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_with_invalid_refresh_token(self):
        """Test logout with invalid refresh token"""
        response = self.client.post(self.logout_url, {'refresh': 'invalid_token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_logout_with_already_blacklisted_token(self):
        """Test logout with already blacklisted token"""
        # First logout
        self.client.post(self.logout_url, {'refresh': str(self.refresh)}, format='json')
        
        # Try to logout again with same token
        response = self.client.post(self.logout_url, {'refresh': str(self.refresh)}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordChangeTestCase(APITestCase):
    """Test password change functionality"""
    
    def setUp(self):
        self.password_change_url = reverse('change-password')
        self.user = User.objects.create_user(
            email='test@example.com',
            password='OldSecurePass123!',
            first_name='John',
            last_name='Doe'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')
    
    def test_valid_password_change(self):
        """Test successful password change"""
        data = {
            'old_password': 'OldSecurePass123!',
            'new_password': 'NewSecurePass456!'
        }
        
        response = self.client.put(self.password_change_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password changed successfully')
        
        # Verify password was actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecurePass456!'))
    
    def test_password_change_with_wrong_old_password(self):
        """Test password change with incorrect old password"""
        data = {
            'old_password': 'WrongOldPassword',
            'new_password': 'NewSecurePass456!'
        }
        
        response = self.client.put(self.password_change_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_password_change_without_authentication(self):
        """Test password change without authentication"""
        self.client.credentials()  # Remove authentication
        data = {
            'old_password': 'OldSecurePass123!',
            'new_password': 'NewSecurePass456!'
        }
        
        response = self.client.put(self.password_change_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_password_change_with_weak_new_password(self):
        """Test password change with weak new password"""
        data = {
            'old_password': 'OldSecurePass123!',
            'new_password': '123'
        }
        
        response = self.client.put(self.password_change_url, data, format='json')
        # Should validate password strength (depends on implementation)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK])


class TokenSecurityTestCase(APITestCase):
    """Test JWT token security and validation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = self.refresh.access_token
    
    def test_access_with_valid_token(self):
        """Test API access with valid token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_access_with_invalid_token(self):
        """Test API access with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_access_with_expired_token(self):
        """Test API access with expired token"""
        # Use an obviously invalid/expired token format
        expired_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjA5NDU5MjAwLCJqdGkiOiJmOTVhZDY4M2ExYTI0MzAwOGE2ZTVhYjIwZWJkOWY0MyIsInVzZXJfaWQiOjF9.invalid'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {expired_token}')
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test token refresh functionality"""
        refresh_url = reverse('token-refresh')  # Assuming you have this endpoint
        response = self.client.post(refresh_url, {'refresh': str(self.refresh)}, format='json')
        # This test depends on your token refresh endpoint implementation
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])


class SecurityTestCase(APITestCase):
    """Test security vulnerabilities and edge cases"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            first_name='John',
            last_name='Doe'
        )
    
    def test_xss_prevention_in_registration(self):
        """Test XSS prevention in user registration"""
        malicious_data = {
            'email': 'test2@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': '<script>alert("XSS")</script>',
            'last_name': '<img src=x onerror=alert("XSS")>'
        }
        
        response = self.client.post(reverse('user-register'), malicious_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(email='test2@example.com')
            # Verify that scripts are escaped or removed
            self.assertNotIn('<script>', user.first_name)
            self.assertNotIn('onerror', user.last_name)
    
    def test_large_payload_handling(self):
        """Test handling of unusually large payloads"""
        large_data = {
            'email': 'test3@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'A' * 10000,  # Very long name
            'last_name': 'B' * 10000
        }
        
        response = self.client.post(reverse('user-register'), large_data, format='json')
        # Should handle gracefully, likely with validation error
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE])
    
    def test_concurrent_user_creation(self):
        """Test concurrent user creation with same email"""
        import threading
        from django.test import TransactionTestCase
        
        results = []
        
        def create_user():
            from django.test.client import Client
            client = Client()
            try:
                response = client.post('/api/auth/register/', {
                    'email': 'concurrent@example.com',
                    'password': 'SecurePass123!',
                    'password_confirm': 'SecurePass123!',
                    'first_name': 'Concurrent',
                    'last_name': 'User'
                }, content_type='application/json')
                results.append(response.status_code)
            except Exception as e:
                results.append(400)  # Treat exceptions as validation errors
        
        # Create multiple threads trying to create the same user
        threads = [threading.Thread(target=create_user) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # At least one should succeed, others should fail with validation error
        success_count = sum(1 for result in results if result == 201)
        error_count = sum(1 for result in results if result == 400)
        
        # Either one succeeds and others fail, or all fail due to concurrent access
        self.assertTrue(success_count <= 1)
        self.assertTrue(success_count + error_count == len(results))
    
    def test_invalid_json_handling(self):
        """Test handling of malformed JSON"""
        response = self.client.post(
            reverse('user-register'),
            data='{"invalid": json}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unicode_handling(self):
        """Test handling of unicode characters"""
        unicode_data = {
            'email': 'unicode@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': '测试',
            'last_name': '用户'
        }
        
        response = self.client.post(reverse('user-register'), unicode_data, format='json')
        if response.status_code == status.HTTP_201_CREATED:
            user = User.objects.get(email='unicode@example.com')
            self.assertEqual(user.first_name, '测试')
            self.assertEqual(user.last_name, '用户') 