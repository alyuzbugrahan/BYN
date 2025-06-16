from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create demo users for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if users exist',
        )

    def handle(self, *args, **options):
        """Create demo users for production"""
        
        demo_users = [
            {
                'email': 'test@example.com',
                'password': 'Test1234!',
                'first_name': 'Demo',
                'last_name': 'User',
                'headline': 'Frontend Demo Account',
                'location': 'San Francisco, CA',
                'about': 'This is a demo account for testing the BYN LinkedIn Clone application.',
                'is_active': True,
            },
            {
                'email': 'john.doe@example.com',
                'password': 'testpass123',
                'first_name': 'John',
                'last_name': 'Doe',
                'headline': 'Software Engineer at Tech Corp',
                'location': 'San Francisco, CA',
                'about': 'Passionate software engineer with 5+ years of experience in full-stack development.',
                'is_active': True,
            },
            {
                'email': 'jane.smith@example.com',
                'password': 'testpass123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'headline': 'Product Manager at Innovation Inc',
                'location': 'New York, NY',
                'about': 'Product manager focused on user experience and data-driven decisions.',
                'is_active': True,
            },
            {
                'email': 'mike.wilson@example.com',
                'password': 'testpass123',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'headline': 'Data Scientist at Analytics Pro',
                'location': 'Seattle, WA',
                'about': 'Data scientist specializing in machine learning and predictive analytics.',
                'is_active': True,
            }
        ]

        created_count = 0
        
        with transaction.atomic():
            for user_data in demo_users:
                email = user_data['email']
                
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    if options['force']:
                        User.objects.filter(email=email).delete()
                        self.stdout.write(
                            self.style.WARNING(f'Deleted existing user: {email}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'User already exists: {email} (use --force to recreate)')
                        )
                        continue
                
                # Create the user
                password = user_data.pop('password')
                user = User.objects.create_user(**user_data)
                user.set_password(password)
                user.save()
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created demo user: {email}')
                )
        
        # Create superuser if specified via environment
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if admin_email and admin_password:
            if not User.objects.filter(email=admin_email, is_superuser=True).exists():
                User.objects.create_superuser(
                    email=admin_email,
                    password=admin_password,
                    first_name='Admin',
                    last_name='User'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created admin user: {admin_email}')
                )
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} users!')
        )
        self.stdout.write(
            self.style.SUCCESS('Demo users are ready for frontend testing.')
        ) 