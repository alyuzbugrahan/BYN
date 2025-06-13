#!/usr/bin/env python
"""
Comprehensive startup script for LinkedIn Clone
This script initializes all sample data when the system starts up
Run this with: python initialize_sample_data.py
"""

import os
import sys
import django
import subprocess
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkedin_clone.settings')
django.setup()

from accounts.models import User
from companies.models import Company
from jobs.models import Job
from feed.models import Post, Comment, Hashtag
from connections.models import Connection

class SampleDataInitializer:
    def __init__(self):
        self.script_dir = '/app'
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def check_existing_data(self):
        """Check if sample data already exists"""
        self.log("🔍 Checking existing data...")
        
        stats = {
            'users': User.objects.count(),
            'companies': Company.objects.count(),
            'jobs': Job.objects.count(),
            'posts': Post.objects.count(),
            'comments': Comment.objects.count(),
            'connections': Connection.objects.count(),
            'users_with_photos': User.objects.filter(profile_picture__isnull=False).count(),
            'companies_with_logos': Company.objects.filter(logo__isnull=False).count(),
        }
        
        self.log(f"Current data: Users:{stats['users']}, Companies:{stats['companies']}, Jobs:{stats['jobs']}, Posts:{stats['posts']}")
        return stats
        
    def run_script(self, script_name, description):
        """Run a Python script and handle errors"""
        self.log(f"🔄 {description}...")
        
        try:
            script_path = os.path.join(self.script_dir, script_name)
            if not os.path.exists(script_path):
                self.log(f"⚠️  Script not found: {script_path}", "WARNING")
                return False
                
            result = subprocess.run([
                sys.executable, script_path
            ], capture_output=True, text=True, cwd=self.script_dir)
            
            if result.returncode == 0:
                self.log(f"✅ {description} completed successfully")
                if result.stdout:
                    # Print last few lines of output
                    lines = result.stdout.strip().split('\n')[-3:]
                    for line in lines:
                        if line.strip():
                            self.log(f"   {line}", "OUTPUT")
                return True
            else:
                self.log(f"❌ {description} failed", "ERROR")
                self.log(f"Error: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error running {script_name}: {str(e)}", "ERROR")
            return False
            
    def run_management_command(self, command, description):
        """Run a Django management command"""
        self.log(f"🔄 {description}...")
        
        try:
            result = subprocess.run([
                sys.executable, 'manage.py'
            ] + command, capture_output=True, text=True, cwd=self.script_dir)
            
            if result.returncode == 0:
                self.log(f"✅ {description} completed successfully")
                if result.stdout:
                    # Print last few lines of output
                    lines = result.stdout.strip().split('\n')[-2:]
                    for line in lines:
                        if line.strip():
                            self.log(f"   {line}", "OUTPUT")
                return True
            else:
                self.log(f"❌ {description} failed", "ERROR")
                self.log(f"Error: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error running management command: {str(e)}", "ERROR")
            return False
    
    def initialize_all_data(self, force=False):
        """Initialize all sample data in the correct order"""
        self.log("🚀 Starting LinkedIn Clone Sample Data Initialization")
        self.log("=" * 60)
        
        # Check existing data
        initial_stats = self.check_existing_data()
        
        # Determine what needs to be created
        needs_basic_data = initial_stats['users'] < 4 or initial_stats['companies'] < 3
        needs_photos = initial_stats['users_with_photos'] < initial_stats['users']
        needs_feed_data = initial_stats['posts'] < 20
        needs_connections = initial_stats['connections'] < 3
        
        if not force and not any([needs_basic_data, needs_photos, needs_feed_data, needs_connections]):
            self.log("ℹ️  Sample data already exists. Use force=True to recreate.")
            self.show_final_summary()
            return True
        
        success_count = 0
        total_steps = 0
        
        # Step 1: Create basic data (users, companies, jobs, skills)
        if needs_basic_data or force:
            total_steps += 1
            if self.run_script('create_sample_data.py', 'Creating basic sample data (users, companies, jobs)'):
                success_count += 1
            time.sleep(2)  # Small delay between steps
        
        # Step 2: Add profile photos and company logos
        if needs_photos or force:
            total_steps += 1
            if self.run_script('add_profile_photos.py', 'Adding profile photos and company logos'):
                success_count += 1
            time.sleep(2)
        
        # Step 3: Create feed data (posts, comments, hashtags)
        if needs_feed_data or force:
            total_steps += 1
            if self.run_management_command(
                ['create_sample_feed_data', '--posts', '30', '--comments', '80'],
                'Creating advanced feed data (posts, comments, hashtags)'
            ):
                success_count += 1
            time.sleep(2)
        
        # Step 4: Create connections between users
        if needs_connections or force:
            total_steps += 1
            if self.run_script('create_more_connections.py', 'Creating user connections and network'):
                success_count += 1
            time.sleep(2)
        
        # Step 5: Test connections system (optional but good for verification)
        total_steps += 1
        if self.run_script('test_connections.py', 'Testing and verifying connection system'):
            success_count += 1
        
        # Final summary
        self.log(f"\n📊 Initialization Summary: {success_count}/{total_steps} steps completed successfully")
        
        if success_count == total_steps:
            self.log("🎉 All sample data initialized successfully!")
            self.show_final_summary()
            return True
        else:
            self.log("⚠️  Some steps failed. Check logs above for details.", "WARNING")
            return False
    
    def show_final_summary(self):
        """Show final data summary"""
        self.log("\n📋 Final Data Summary:")
        self.log("-" * 30)
        
        final_stats = self.check_existing_data()
        
        self.log(f"👥 Users: {final_stats['users']}")
        self.log(f"🏢 Companies: {final_stats['companies']}")
        self.log(f"💼 Jobs: {final_stats['jobs']}")
        self.log(f"📝 Posts: {final_stats['posts']}")
        self.log(f"💬 Comments: {final_stats['comments']}")
        self.log(f"🤝 Connections: {final_stats['connections']}")
        self.log(f"📸 Users with photos: {final_stats['users_with_photos']}/{final_stats['users']}")
        self.log(f"🖼️  Companies with logos: {final_stats['companies_with_logos']}/{final_stats['companies']}")
        
        self.log(f"\n🌐 Your LinkedIn Clone is ready!")
        self.log(f"Frontend: http://localhost:3000")
        self.log(f"Backend API: http://localhost:8000/api/")
        self.log(f"Admin Panel: http://localhost:8000/admin")

def main():
    """Main function"""
    initializer = SampleDataInitializer()
    
    # Check command line arguments
    force = '--force' in sys.argv or '-f' in sys.argv
    
    if force:
        initializer.log("🔄 Force mode enabled - will recreate all data")
    
    try:
        # Wait a moment for database to be ready
        initializer.log("⏳ Waiting for database to be ready...")
        time.sleep(5)
        
        # Run initialization
        success = initializer.initialize_all_data(force=force)
        
        if success:
            initializer.log("✅ Sample data initialization completed successfully!")
            sys.exit(0)
        else:
            initializer.log("❌ Sample data initialization failed!", "ERROR")
            sys.exit(1)
            
    except KeyboardInterrupt:
        initializer.log("❌ Initialization interrupted by user", "ERROR")
        sys.exit(1)
    except Exception as e:
        initializer.log(f"❌ Unexpected error: {str(e)}", "ERROR")
        sys.exit(1)

if __name__ == '__main__':
    main() 