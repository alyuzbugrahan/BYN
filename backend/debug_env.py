#!/usr/bin/env python
"""
Debug script to check environment variables on Railway
"""
import os

print("=== ENVIRONMENT VARIABLES DEBUG ===")
print()

# Check for DATABASE related variables
print("🔍 DATABASE VARIABLES:")
for key, value in os.environ.items():
    if 'DATABASE' in key.upper() or 'DB_' in key.upper() or 'POSTGRES' in key.upper():
        # Hide password but show structure
        if 'PASSWORD' in key.upper() and value:
            display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
        else:
            display_value = value[:100] + "..." if len(value) > 100 else value
        print(f"  {key} = {display_value}")

print()
print("🔍 RAILWAY VARIABLES:")
for key, value in os.environ.items():
    if 'RAILWAY' in key.upper():
        print(f"  {key} = {value}")

print()
print("🔍 DJANGO SETTINGS:")
try:
    import django
    django.setup()
    from django.conf import settings
    print(f"  DEBUG = {settings.DEBUG}")
    print(f"  SECRET_KEY configured = {bool(settings.SECRET_KEY)}")
    print(f"  Database engine = {settings.DATABASES['default']['ENGINE']}")
    print(f"  Database name = {settings.DATABASES['default'].get('NAME', 'Not set')}")
    print(f"  Database host = {settings.DATABASES['default'].get('HOST', 'Not set')}")
except Exception as e:
    print(f"  Error loading Django settings: {e}")

print()
print("=== END DEBUG ===") 