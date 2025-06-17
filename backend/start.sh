#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting BYN Django Application for Railway..."
echo "=================================================="

# Set default port if not provided by Railway
export PORT=${PORT:-8000}

echo "📡 Port: $PORT"
echo "🗄️  Database URL: ${DATABASE_URL:0:20}..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
while ! python manage.py dbshell --command="SELECT 1;" >/dev/null 2>&1; do
    echo "⏳ Database not ready yet, waiting 2 seconds..."
    sleep 2
done
echo "✅ Database connection established!"

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Check if we should initialize sample data
if [ "$INITIALIZE_SAMPLE_DATA" = "true" ] || [ "$INITIALIZE_SAMPLE_DATA" = "1" ]; then
    echo "🎯 Initializing sample data..."
    python initialize_sample_data.py || echo "⚠️  Sample data initialization failed"
elif [ "$FORCE_SAMPLE_DATA" = "true" ] || [ "$FORCE_SAMPLE_DATA" = "1" ]; then
    echo "🔄 Force initializing sample data..."
    python initialize_sample_data.py --force || echo "⚠️  Sample data initialization failed"
else
    echo "ℹ️  Skipping sample data initialization"
fi

# Create superuser if it doesn't exist and credentials are provided
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creating superuser if it doesn't exist..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('✅ Superuser created successfully!')
else:
    print('ℹ️  Superuser already exists')
" || echo "⚠️  Superuser creation failed"
fi

echo "🎉 Starting Gunicorn server on port $PORT..."
echo "=================================================="

# Start the application with Gunicorn
exec gunicorn byn.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - 