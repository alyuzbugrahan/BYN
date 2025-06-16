# Local development settings using SQLite
from .settings import *

# Override database for local development with SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Local development settings
DEBUG = True
SECRET_KEY = 'django-insecure-local-development-key-only'

# Simpler middleware for local development
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Simple static files for local dev
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Local CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Disable complex features for local development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

print("🔧 Using LOCAL development settings with SQLite database") 