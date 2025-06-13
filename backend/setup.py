#!/usr/bin/env python3
"""
Setup script for LinkedIn Clone project
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and print its description"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def main():
    print("🚀 Setting up LinkedIn Clone project...")
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("\n⚠️  Virtual environment not found!")
        print("Please create a virtual environment first:")
        print("python -m venv venv")
        print("venv\\Scripts\\activate  # On Windows")
        print("source venv/bin/activate  # On Unix/macOS")
        sys.exit(1)
    
    # Install dependencies
    run_command("pip install -r requirements.txt", "Installing Python dependencies")
    
    # Create migrations
    run_command("python manage.py makemigrations", "Creating database migrations")
    
    # Apply migrations
    run_command("python manage.py migrate", "Applying database migrations")
    
    # Create superuser (optional)
    print("\n📝 You can now create a superuser account:")
    print("python manage.py createsuperuser")
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy env_example.txt to .env and configure your environment variables")
    print("2. Set up your PostgreSQL database")
    print("3. Create a superuser: python manage.py createsuperuser")
    print("4. Run the development server: python manage.py runserver")
    print("5. Visit http://127.0.0.1:8000/api/schema/swagger-ui/ for API documentation")

if __name__ == "__main__":
    main() 