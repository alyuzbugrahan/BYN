from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Check database connectivity and print debug information'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking database configuration...")
        
        # Print environment variables
        self.stdout.write("\n📋 Environment Variables:")
        for key in ['DATABASE_URL', 'POSTGRES_URL', 'RAILWAY_ENVIRONMENT', 'PORT']:
            value = os.environ.get(key, 'Not set')
            if key in ['DATABASE_URL', 'POSTGRES_URL'] and value != 'Not set':
                # Mask the password for security
                if '@' in value:
                    masked = value.split('@')[0].split(':')[:-1]
                    masked.append('****@')
                    masked.append(value.split('@')[1])
                    value = ':'.join(masked)
            self.stdout.write(f"  {key}: {value}")
        
        # Check database configuration
        self.stdout.write("\n🔧 Database Configuration:")
        db_config = settings.DATABASES['default']
        for key, value in db_config.items():
            if key == 'PASSWORD':
                value = '****' if value else 'Not set'
            self.stdout.write(f"  {key}: {value}")
        
        # Test database connection
        self.stdout.write("\n🔌 Testing database connection...")
        try:
            db_conn = connections['default']
            with db_conn.cursor() as cursor:
                cursor.execute('SELECT 1')
                result = cursor.fetchone()
                if result[0] == 1:
                    self.stdout.write(self.style.SUCCESS("✅ Database connection successful!"))
                else:
                    self.stdout.write(self.style.ERROR("❌ Database connection failed - unexpected result"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Database connection failed: {e}"))
            
            # Provide specific troubleshooting tips
            self.stdout.write("\n🚨 Troubleshooting Tips:")
            if "Name or service not known" in str(e):
                self.stdout.write("  • Check if PostgreSQL service is running in Railway")
                self.stdout.write("  • Verify DATABASE_URL environment variable is set")
                self.stdout.write("  • Ensure PostgreSQL service is linked to your app")
            elif "connection refused" in str(e):
                self.stdout.write("  • PostgreSQL service might be down")
                self.stdout.write("  • Check Railway service status")
            elif "authentication failed" in str(e):
                self.stdout.write("  • Check DATABASE_URL credentials")
                self.stdout.write("  • Verify PostgreSQL user permissions") 