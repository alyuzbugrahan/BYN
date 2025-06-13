#!/usr/bin/env python
"""
Script to add profile photos for users and company logos
"""
import os
import django
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkedin_clone.settings')
django.setup()

from accounts.models import User
from companies.models import Company
from django.db import models

def download_image(url, timeout=10):
    """Download image from URL and return file content"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return None

def add_user_profile_photos():
    """Add profile photos to users"""
    
    # Get all users and check if they need photos
    all_users = User.objects.all()
    users = []
    
    for user in all_users:
        if not user.profile_picture or not user.profile_picture.name:
            users.append(user)
    
    if not users:
        print("ℹ️  All users already have profile pictures")
        return
    
    print(f"📸 Adding profile photos for {len(users)} users...")
    
    # Different photo styles for variety
    photo_styles = [
        "https://picsum.photos/300/300?random=",
        "https://thispersondoesnotexist.com/",  # AI-generated faces (backup option)
        "https://randomuser.me/api/portraits/men/",  # Random User API
        "https://randomuser.me/api/portraits/women/",
    ]
    
    # Use Lorem Picsum for consistent, professional photos
    success_count = 0
    
    for i, user in enumerate(users):
        try:
            # Generate a random photo URL
            photo_id = random.randint(1, 1000)
            url = f"https://picsum.photos/300/300?random={photo_id}&grayscale"
            
            # Download the image
            image_content = download_image(url)
            
            if image_content:
                # Save the image
                filename = f"profile_{user.id}_{photo_id}.jpg"
                file_content = ContentFile(image_content.getvalue())
                
                # Save to the profile_picture field
                user.profile_picture.save(filename, file_content, save=True)
                
                print(f"✅ Added photo for {user.full_name}")
                success_count += 1
            else:
                print(f"⚠️  Failed to download photo for {user.full_name}")
                
        except Exception as e:
            print(f"❌ Error adding photo for {user.full_name}: {e}")
    
    print(f"📸 Successfully added {success_count} profile photos!")

def add_company_logos():
    """Add logos to companies"""
    
    # Get all companies and check if they need logos
    all_companies = Company.objects.all()
    companies = []
    
    for company in all_companies:
        if not company.logo or not company.logo.name:
            companies.append(company)
    
    if not companies:
        print("ℹ️  All companies already have logos")
        return
    
    print(f"🏢 Adding logos for {len(companies)} companies...")
    
    # Company logo styles - more geometric/business-like
    success_count = 0
    
    for i, company in enumerate(companies):
        try:
            # Generate a logo-style image (more geometric/abstract)
            logo_id = random.randint(1, 500)
            # Using geometric patterns for company logos
            url = f"https://picsum.photos/200/200?random={logo_id}&blur=1"
            
            # Download the image
            image_content = download_image(url)
            
            if image_content:
                # Save the image
                filename = f"logo_{company.id}_{logo_id}.jpg"
                file_content = ContentFile(image_content.getvalue())
                
                # Save to the logo field
                company.logo.save(filename, file_content, save=True)
                
                print(f"✅ Added logo for {company.name}")
                success_count += 1
            else:
                print(f"⚠️  Failed to download logo for {company.name}")
                
        except Exception as e:
            print(f"❌ Error adding logo for {company.name}: {e}")
    
    print(f"🏢 Successfully added {success_count} company logos!")

def create_profile_photos():
    """Main function to add all profile photos"""
    
    print("🖼️  Adding profile photos and company logos...")
    print("=" * 50)
    
    # Add user profile photos
    add_user_profile_photos()
    print()
    
    # Add company logos
    add_company_logos()
    print()
    
    # Final statistics
    total_users = User.objects.count()
    total_companies = Company.objects.count()
    
    # Count users with actual photos
    users_with_photos = 0
    for user in User.objects.all():
        if user.profile_picture and user.profile_picture.name:
            users_with_photos += 1
    
    # Count companies with actual logos
    companies_with_logos = 0
    for company in Company.objects.all():
        if company.logo and company.logo.name:
            companies_with_logos += 1
    
    print("📊 Final Statistics:")
    print(f"👥 Users with photos: {users_with_photos}/{total_users}")
    print(f"🏢 Companies with logos: {companies_with_logos}/{total_companies}")
    
    if users_with_photos == total_users and companies_with_logos == total_companies:
        print("\n🎉 All profile photos and logos added successfully!")
    
    print(f"\n🌐 Visit your frontend at http://localhost:3000 to see the photos!")
    print(f"🔧 Admin panel: http://localhost:8000/admin")

if __name__ == '__main__':
    create_profile_photos() 