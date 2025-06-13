#!/bin/bash
set -e

echo "🚀 Starting LinkedIn Clone Backend..."
echo "======================================"

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

# Collect static files (for production)
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "⚠️  Static files collection failed (this is normal in development)"

# Check if we should initialize sample data
if [ "$INITIALIZE_SAMPLE_DATA" = "true" ] || [ "$INITIALIZE_SAMPLE_DATA" = "1" ]; then
    echo "🎯 Initializing sample data..."
    python initialize_sample_data.py
elif [ "$FORCE_SAMPLE_DATA" = "true" ] || [ "$FORCE_SAMPLE_DATA" = "1" ]; then
    echo "🔄 Force initializing sample data..."
    python initialize_sample_data.py --force
else
    echo "ℹ️  Skipping sample data initialization (set INITIALIZE_SAMPLE_DATA=true to enable)"
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
"
fi

echo "🎉 Backend initialization completed!"
echo "======================================"

# Start the Django development server
exec "$@" 