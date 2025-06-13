#!/usr/bin/env python
"""
API Testing Script for LinkedIn Clone
This script demonstrates all the implemented features and endpoints.
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://127.0.0.1:8000/api"

def print_response(title, response):
    """Helper function to print API responses"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(response.text)
    else:
        print(f"Error: {response.text}")

def test_authentication():
    """Test user authentication endpoints"""
    print("\n🔐 TESTING AUTHENTICATION")
    
    # Test user registration
    register_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpass123",
        "password_confirm": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print_response("User Registration", response)
    
    # Test user login
    login_data = {
        "email": "john.doe@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print_response("User Login", response)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access']
    
    return None

def test_user_profiles(token):
    """Test user profile endpoints"""
    print("\n👤 TESTING USER PROFILES")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get current user profile
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    print_response("Current User Profile", response)
    
    # Search users
    response = requests.get(f"{BASE_URL}/users/search/?q=developer", headers=headers)
    print_response("User Search", response)
    
    # Get specific user profile
    response = requests.get(f"{BASE_URL}/users/profile/2/", headers=headers)
    print_response("Specific User Profile", response)

def test_job_system(token):
    """Test job-related endpoints"""
    print("\n💼 TESTING JOB SYSTEM")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # List all jobs
    response = requests.get(f"{BASE_URL}/jobs/jobs/", headers=headers)
    print_response("Job Listings", response)
    
    # Get job categories
    response = requests.get(f"{BASE_URL}/jobs/categories/", headers=headers)
    print_response("Job Categories", response)
    
    # Filter jobs by location
    response = requests.get(f"{BASE_URL}/jobs/jobs/?location=San Francisco", headers=headers)
    print_response("Jobs Filtered by Location", response)
    
    # Filter jobs by skills
    response = requests.get(f"{BASE_URL}/jobs/jobs/?skills=Python,Django", headers=headers)
    print_response("Jobs Filtered by Skills", response)
    
    # Get job detail
    response = requests.get(f"{BASE_URL}/jobs/jobs/1/", headers=headers)
    print_response("Job Detail", response)
    
    # Get recommended jobs
    response = requests.get(f"{BASE_URL}/jobs/jobs/recommended/", headers=headers)
    print_response("Recommended Jobs", response)
    
    # Save a job
    response = requests.post(f"{BASE_URL}/jobs/jobs/1/save/", headers=headers)
    print_response("Save Job", response)
    
    # Get saved jobs
    response = requests.get(f"{BASE_URL}/jobs/jobs/saved/", headers=headers)
    print_response("Saved Jobs", response)
    
    # Apply for a job
    application_data = {
        "job_id": 1,
        "cover_letter": "I am very interested in this position and believe my skills in Python and Django make me a great fit.",
        "portfolio_url": "https://github.com/johndoe"
    }
    response = requests.post(f"{BASE_URL}/jobs/applications/", json=application_data, headers=headers)
    print_response("Job Application", response)
    
    # Get user's applications
    response = requests.get(f"{BASE_URL}/jobs/applications/", headers=headers)
    print_response("User's Job Applications", response)
    
    # Get job statistics
    response = requests.get(f"{BASE_URL}/jobs/stats/", headers=headers)
    print_response("Job Statistics", response)

def test_user_skills(token):
    """Test user skills management"""
    print("\n🎯 TESTING SKILLS MANAGEMENT")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add a skill
    skill_data = {"skill_name": "FastAPI"}
    response = requests.post(f"{BASE_URL}/users/skills/", json=skill_data, headers=headers)
    print_response("Add Skill", response)
    
    # Get user's skills
    response = requests.get(f"{BASE_URL}/users/skills/", headers=headers)
    print_response("User's Skills", response)

def test_experience_education(token):
    """Test experience and education management"""
    print("\n🎓 TESTING EXPERIENCE & EDUCATION")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add experience
    experience_data = {
        "title": "Software Developer",
        "company": "ABC Tech",
        "location": "Remote",
        "start_date": "2022-01-01",
        "is_current": True,
        "description": "Working on web applications using Django and React"
    }
    response = requests.post(f"{BASE_URL}/users/experiences/", json=experience_data, headers=headers)
    print_response("Add Experience", response)
    
    # Get experiences
    response = requests.get(f"{BASE_URL}/users/experiences/", headers=headers)
    print_response("User's Experiences", response)
    
    # Add education
    education_data = {
        "school": "University of Technology",
        "degree": "Bachelor of Science",
        "field_of_study": "Computer Science",
        "start_year": 2018,
        "end_year": 2022
    }
    response = requests.post(f"{BASE_URL}/users/education/", json=education_data, headers=headers)
    print_response("Add Education", response)
    
    # Get education
    response = requests.get(f"{BASE_URL}/users/education/", headers=headers)
    print_response("User's Education", response)

def main():
    """Main test function"""
    print("🚀 LINKEDIN CLONE API TESTING")
    print("=" * 60)
    
    # Test authentication and get token
    token = test_authentication()
    
    if not token:
        print("❌ Authentication failed. Cannot proceed with other tests.")
        return
    
    print(f"\n✅ Authentication successful! Token obtained.")
    
    # Run all tests
    test_user_profiles(token)
    test_job_system(token)
    test_user_skills(token)
    test_experience_education(token)
    
    print("\n🎉 ALL TESTS COMPLETED!")
    print("\n📝 Available endpoints to test:")
    print("- Authentication: /api/auth/")
    print("- User Profiles: /api/users/")
    print("- Job System: /api/jobs/")
    print("- API Documentation: http://127.0.0.1:8000/api/schema/swagger-ui/")
    print("- Admin Panel: http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    main() 