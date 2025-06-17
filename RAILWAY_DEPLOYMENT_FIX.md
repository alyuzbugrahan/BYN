# Railway Deployment Fix Guide

## Issues Fixed

1. **Health Check Path Mismatch**: Updated `railway.json` to use `/api/` instead of `/health/`
2. **DRF Spectacular Warnings**: Fixed missing type hints for `is_reply` and `engagement_rate` methods
3. **Docker Configuration**: Improved Dockerfile with proper user permissions
4. **Startup Script**: Enhanced start.sh with better logging and error handling

## Changes Made

### 1. Railway Configuration (`railway.json`)
- ✅ Changed healthcheck path from `/health/` to `/api/`
- ✅ Set builder to use DOCKERFILE instead of NIXPACKS for better control

### 2. Feed Serializers (`feed/serializers.py`)
- ✅ Added `@extend_schema_field(bool)` decorator to `get_is_reply` method
- ✅ Added `@extend_schema_field(float)` decorator to `get_engagement_rate` method
- ✅ Fixed DRF Spectacular warnings

### 3. Docker Configuration (`Dockerfile`)
- ✅ Added non-root user for security
- ✅ Fixed port exposure
- ✅ Improved startup command

### 4. Startup Script (`start.sh`)
- ✅ Added detailed logging for debugging
- ✅ Improved Gunicorn configuration
- ✅ Added worker class specification

## Environment Variables Required

Set these in your Railway project:

```bash
# Required
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
DEBUG=False

# Optional but recommended
DJANGO_LOG_LEVEL=INFO
CORS_ALLOW_ALL_ORIGINS=True
RAILWAY_ENVIRONMENT=production
```

## Deployment Steps

1. **Push your changes** to your repository
2. **Set environment variables** in Railway dashboard
3. **Redeploy** your Railway service

## Testing the Deployment

Once deployed, your endpoints should be accessible:

- Health check: `https://your-app.railway.app/api/`
- API docs: `https://your-app.railway.app/api/schema/swagger-ui/`
- Admin: `https://your-app.railway.app/admin/`

## Common Issues & Solutions

### 1. Database Connection Issues
- Railway automatically provides `DATABASE_URL`
- Make sure your PostgreSQL service is running

### 2. Static Files Not Loading
- The app uses WhiteNoise for static file serving
- Static files are collected during startup

### 3. CORS Issues
- Set `CORS_ALLOWED_ORIGINS` to include your frontend domain
- Or use `CORS_ALLOW_ALL_ORIGINS=True` for development

### 4. Health Check Still Failing
- Check Railway logs for detailed error messages
- Ensure the `/api/` endpoint returns JSON response

## Debug Commands

If deployment still fails, check Railway logs for:

```bash
# Database connection
✅ Database connection established!

# Migrations
🔄 Running database migrations...

# Static files
📦 Collecting static files...

# Gunicorn startup
🚀 Starting Gunicorn server...
```

## Next Steps

After successful deployment:

1. Create a superuser via Railway's database console
2. Test all API endpoints
3. Configure your frontend to use the Railway backend URL
4. Set up proper environment variables for production

## Support

If issues persist:
1. Check Railway deployment logs
2. Verify all environment variables are set
3. Ensure PostgreSQL service is connected
4. Test the health endpoint directly in browser 