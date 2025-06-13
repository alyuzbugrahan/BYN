#!/usr/bin/env python
"""
Script to create sample data for LinkedIn Clone
Run this with: python create_sample_data.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkedin_clone.settings')
django.setup()

from accounts.models import User, Skill, Experience, Education, UserSkill
from companies.models import Industry, Company
from jobs.models import JobCategory, Job

# Create industries
print("Creating industries...")
tech_industry = Industry.objects.create(name="Technology")
finance_industry = Industry.objects.create(name="Financial Services")
healthcare_industry = Industry.objects.create(name="Healthcare")

# Create skills
print("Creating skills...")
skills_data = [
    "Python", "JavaScript", "React", "Django", "Node.js", "SQL", "PostgreSQL",
    "AWS", "Docker", "Kubernetes", "Git", "REST APIs", "GraphQL", "TypeScript",
    "Machine Learning", "Data Analysis", "Project Management", "Leadership"
]

skills = []
for skill_name in skills_data:
    skill, created = Skill.objects.get_or_create(name=skill_name)
    skills.append(skill)

# Create users
print("Creating users...")
users_data = [
    {
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "headline": "Senior Software Engineer at TechCorp",
        "current_position": "Senior Software Engineer",
        "industry": "Technology",
        "experience_level": "mid",
        "location": "San Francisco, CA"
    },
    {
        "email": "jane.smith@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "headline": "Product Manager | AI & Machine Learning",
        "current_position": "Product Manager",
        "industry": "Technology",
        "experience_level": "mid",
        "location": "New York, NY"
    },
    {
        "email": "mike.wilson@example.com",
        "first_name": "Mike",
        "last_name": "Wilson",
        "headline": "Full Stack Developer | React & Django",
        "current_position": "Full Stack Developer",
        "industry": "Technology",
        "experience_level": "associate",
        "location": "Austin, TX"
    }
]

users = []
for user_data in users_data:
    user = User.objects.create_user(
        email=user_data["email"],
        password="testpass123",
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        headline=user_data["headline"],
        current_position=user_data["current_position"],
        industry=user_data["industry"],
        experience_level=user_data["experience_level"],
        location=user_data["location"]
    )
    users.append(user)

# Create superuser if not exists
if not User.objects.filter(email="admin@example.com").exists():
    admin_user = User.objects.create_superuser(
        email="admin@example.com",
        password="admin123",
        first_name="Admin",
        last_name="User"
    )
    users.append(admin_user)

print(f"Created {len(users)} users")

# Add skills to users
print("Adding skills to users...")
john = users[0]
jane = users[1]
mike = users[2]

# John's skills (Senior Software Engineer)
john_skills = ["Python", "Django", "PostgreSQL", "AWS", "Docker", "REST APIs"]
for skill_name in john_skills:
    skill = Skill.objects.get(name=skill_name)
    UserSkill.objects.create(user=john, skill=skill)

# Jane's skills (Product Manager)
jane_skills = ["Project Management", "Leadership", "Python", "Data Analysis", "Machine Learning"]
for skill_name in jane_skills:
    skill = Skill.objects.get(name=skill_name)
    UserSkill.objects.create(user=jane, skill=skill)

# Mike's skills (Full Stack Developer)
mike_skills = ["JavaScript", "React", "TypeScript", "Node.js", "Python", "Django"]
for skill_name in mike_skills:
    skill = Skill.objects.get(name=skill_name)
    UserSkill.objects.create(user=mike, skill=skill)

# Create companies
print("Creating companies...")
companies_data = [
    {
        "name": "TechCorp",
        "description": "Leading technology company specializing in AI and cloud solutions.",
        "industry": tech_industry,
        "company_size": "1001-5000",
        "headquarters": "San Francisco, CA",
        "founded_year": 2010,
        "website": "https://techcorp.example.com"
    },
    {
        "name": "InnovateLabs",
        "description": "Startup focused on innovative software solutions for businesses.",
        "industry": tech_industry,
        "company_size": "51-200",
        "headquarters": "Austin, TX",
        "founded_year": 2018,
        "website": "https://innovatelabs.example.com"
    },
    {
        "name": "DataFlow Inc",
        "description": "Data analytics and machine learning platform for enterprises.",
        "industry": tech_industry,
        "company_size": "201-500",
        "headquarters": "New York, NY",
        "founded_year": 2015,
        "website": "https://dataflow.example.com"
    }
]

companies = []
for company_data in companies_data:
    company = Company.objects.create(
        name=company_data["name"],
        slug=company_data["name"].lower().replace(" ", "-"),
        description=company_data["description"],
        industry=company_data["industry"],
        company_size=company_data["company_size"],
        headquarters=company_data["headquarters"],
        founded_year=company_data["founded_year"],
        website=company_data["website"],
        created_by=users[0]  # John creates the companies
    )
    companies.append(company)

print(f"Created {len(companies)} companies")

# Create job categories
print("Creating job categories...")
categories_data = [
    {"name": "Software Development", "description": "Software engineering and development roles"},
    {"name": "Product Management", "description": "Product strategy and management positions"},
    {"name": "Data Science", "description": "Data analysis and machine learning roles"},
    {"name": "DevOps", "description": "Infrastructure and deployment engineering"},
    {"name": "Frontend Development", "description": "UI/UX and frontend development"},
]

categories = []
for cat_data in categories_data:
    category = JobCategory.objects.create(
        name=cat_data["name"],
        slug=cat_data["name"].lower().replace(" ", "-"),
        description=cat_data["description"]
    )
    categories.append(category)

# Create jobs
print("Creating jobs...")
jobs_data = [
    {
        "title": "Senior Python Developer",
        "description": "We are seeking a Senior Python Developer to join our growing team...",
        "requirements": "5+ years of Python experience, Django framework, PostgreSQL, AWS",
        "responsibilities": "Develop scalable web applications, mentor junior developers, code reviews",
        "company": companies[0],  # TechCorp
        "location": "San Francisco, CA",
        "workplace_type": "hybrid",
        "job_type": "full_time",
        "experience_level": "mid",
        "category": categories[0],  # Software Development
        "salary_min": 120000,
        "salary_max": 160000,
        "skills_required": ["Python", "Django", "PostgreSQL"],
        "skills_preferred": ["AWS", "Docker", "REST APIs"]
    },
    {
        "title": "React Frontend Developer",
        "description": "Join our frontend team to build amazing user experiences...",
        "requirements": "3+ years React experience, TypeScript, responsive design",
        "responsibilities": "Build responsive web applications, collaborate with designers",
        "company": companies[1],  # InnovateLabs
        "location": "Austin, TX",
        "workplace_type": "remote",
        "job_type": "full_time",
        "experience_level": "associate",
        "category": categories[4],  # Frontend Development
        "salary_min": 90000,
        "salary_max": 120000,
        "skills_required": ["JavaScript", "React", "TypeScript"],
        "skills_preferred": ["Node.js", "GraphQL"]
    },
    {
        "title": "Product Manager - AI Platform",
        "description": "Lead product strategy for our AI and ML platform...",
        "requirements": "MBA or equivalent, 4+ years product management, AI/ML knowledge",
        "responsibilities": "Define product roadmap, work with engineering teams, market analysis",
        "company": companies[2],  # DataFlow Inc
        "location": "New York, NY",
        "workplace_type": "on_site",
        "job_type": "full_time",
        "experience_level": "mid",
        "category": categories[1],  # Product Management
        "salary_min": 140000,
        "salary_max": 180000,
        "skills_required": ["Project Management", "Leadership"],
        "skills_preferred": ["Machine Learning", "Data Analysis"]
    }
]

jobs = []
for job_data in jobs_data:
    # Create job
    job = Job.objects.create(
        title=job_data["title"],
        slug=job_data["title"].lower().replace(" ", "-"),
        description=job_data["description"],
        requirements=job_data["requirements"],
        responsibilities=job_data["responsibilities"],
        company=job_data["company"],
        location=job_data["location"],
        workplace_type=job_data["workplace_type"],
        job_type=job_data["job_type"],
        experience_level=job_data["experience_level"],
        category=job_data["category"],
        salary_min=job_data["salary_min"],
        salary_max=job_data["salary_max"],
        posted_by=users[0]  # John posts all jobs
    )
    
    # Add required skills
    for skill_name in job_data["skills_required"]:
        skill = Skill.objects.get(name=skill_name)
        job.skills_required.add(skill)
    
    # Add preferred skills
    for skill_name in job_data["skills_preferred"]:
        skill = Skill.objects.get(name=skill_name)
        job.skills_preferred.add(skill)
    
    jobs.append(job)

print(f"Created {len(jobs)} jobs")

# Create experience records
print("Creating experience records...")
Experience.objects.create(
    user=john,
    title="Senior Software Engineer",
    company="TechCorp",
    location="San Francisco, CA",
    start_date="2020-01-01",
    is_current=True,
    description="Lead development of microservices architecture..."
)

Experience.objects.create(
    user=jane,
    title="Product Manager",
    company="DataFlow Inc",
    location="New York, NY",
    start_date="2021-03-01",
    is_current=True,
    description="Managing AI platform product development..."
)

# Create education records
print("Creating education records...")
Education.objects.create(
    user=john,
    school="Stanford University",
    degree="Master of Science",
    field_of_study="Computer Science",
    start_year=2015,
    end_year=2017
)

Education.objects.create(
    user=jane,
    school="MIT",
    degree="Bachelor of Science",
    field_of_study="Computer Science",
    start_year=2014,
    end_year=2018
)

print("✅ Sample data created successfully!")
print("\n📊 Summary:")
print(f"- Users: {User.objects.count()}")
print(f"- Companies: {Company.objects.count()}")
print(f"- Jobs: {Job.objects.count()}")
print(f"- Skills: {Skill.objects.count()}")
print(f"- Industries: {Industry.objects.count()}")
print(f"- Job Categories: {JobCategory.objects.count()}")

print("\n🔑 Login credentials:")
print("Admin: admin@example.com / admin123")
print("Test users: john.doe@example.com / testpass123")
print("            jane.smith@example.com / testpass123")
print("            mike.wilson@example.com / testpass123") 