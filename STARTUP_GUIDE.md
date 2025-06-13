# 🚀 LinkedIn Clone Startup & Sample Data Guide

This guide explains how to automatically initialize your LinkedIn Clone with comprehensive sample data on startup.

## 📋 What Gets Created Automatically

When the system starts up with sample data initialization enabled, it creates:

- **👥 Users**: 4 professional users with complete profiles
- **🏢 Companies**: 3 companies with detailed information and logos
- **💼 Jobs**: 3 job listings with full descriptions
- **📝 Posts**: 30+ professional posts with hashtags and engagement
- **💬 Comments**: 80+ comments and replies
- **#️⃣ Hashtags**: 20 trending hashtags
- **🤝 Connections**: Full network connectivity between users
- **📧 Notifications**: 80+ notifications for user interactions
- **📸 Profile Photos**: High-quality profile photos for all users
- **🖼️ Company Logos**: Professional logos for all companies

## 🐳 Docker Startup Options

### Option 1: Development Mode (Automatic Sample Data)
```bash
# Use the development docker-compose file with automatic sample data
docker compose -f docker-compose.dev.yml up -d --build
```

### Option 2: Production Mode (No Sample Data)
```bash
# Use the standard docker-compose file without sample data
docker compose up --build
```

### Option 3: Force Recreate Sample Data
```bash
# Set environment variable to force recreate all sample data
FORCE_SAMPLE_DATA=true docker compose up --build
```

## ⚙️ Environment Variables

You can control the initialization behavior with these environment variables:

```bash
# Enable automatic sample data creation
INITIALIZE_SAMPLE_DATA=true

# Force recreate all sample data (ignores existing data)
FORCE_SAMPLE_DATA=true

# Create superuser automatically
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123
```

## 🔧 Manual Script Execution

You can also run the initialization scripts manually:

### Run All Sample Data Scripts
```bash
# Inside the backend container
docker compose exec backend python initialize_sample_data.py

# Force mode (recreate everything)
docker compose exec backend python initialize_sample_data.py --force
```

### Run Individual Scripts
```bash
# Basic data (users, companies, jobs)
docker compose exec backend python create_sample_data.py

# Profile photos and logos
docker compose exec backend python add_profile_photos.py

# Advanced feed data
docker compose exec backend python manage.py create_sample_feed_data --posts 30 --comments 80

# User connections
docker compose exec backend python create_more_connections.py

# Test connections system
docker compose exec backend python test_connections.py

# View data summary
docker compose exec backend python simple_summary.py
```

## 📊 Monitoring Startup Process

The startup script provides detailed logging:

```bash
# View startup logs
docker compose logs backend -f

# You'll see logs like:
[2024-06-13 10:30:00] [INFO] 🚀 Starting LinkedIn Clone Sample Data Initialization
[2024-06-13 10:30:01] [INFO] 🔍 Checking existing data...
[2024-06-13 10:30:02] [INFO] 🔄 Creating basic sample data (users, companies, jobs)...
[2024-06-13 10:30:05] [INFO] ✅ Creating basic sample data (users, companies, jobs) completed successfully
```

## 🎯 Sample User Credentials

After initialization, you can log in with these credentials:

### Admin User
- **Email**: `admin@example.com`
- **Password**: `admin123`

### Test Users
- **John Doe**: `john.doe@example.com` / `testpass123`
- **Jane Smith**: `jane.smith@example.com` / `testpass123`
- **Mike Wilson**: `mike.wilson@example.com` / `testpass123`

## 🌐 Access Your LinkedIn Clone

After successful startup:

- **🌐 Frontend**: http://localhost:3000
- **🔧 Backend API**: http://localhost:8000/api/
- **⚙️ Admin Panel**: http://localhost:8000/admin
- **📚 API Documentation**: http://localhost:8000/api/schema/

## 🔄 Script Execution Order

The initialization follows this order to ensure dependencies are met:

1. **Database Migration** - Ensure all tables exist
2. **Basic Data Creation** - Users, companies, jobs, skills
3. **Profile Photos** - Download and assign photos/logos
4. **Feed Data** - Posts, comments, hashtags, engagement
5. **Connections** - User network and relationships
6. **Connection Testing** - Verify system integrity

## 🛠️ Customization

### Adding Your Own Sample Data Scripts

1. Create your script in the `backend/` directory
2. Add it to `initialize_sample_data.py` in the appropriate order
3. Follow the existing pattern for error handling and logging

### Modifying Sample Data

- Edit `create_sample_data.py` for basic user/company data
- Modify `feed/management/commands/create_sample_feed_data.py` for posts
- Update `add_profile_photos.py` for different photo sources

## 🚨 Troubleshooting

### Sample Data Not Loading
```bash
# Check if environment variable is set
docker compose exec backend env | grep INITIALIZE_SAMPLE_DATA

# Check logs for errors
docker compose logs backend | grep ERROR

# Manually run initialization
docker compose exec backend python initialize_sample_data.py --force
```

### Database Connection Issues
```bash
# Check database status
docker compose ps db

# Check database logs
docker compose logs db

# Test database connection
docker compose exec backend python manage.py dbshell
```

### Photo Download Issues
```bash
# Check internet connection from container
docker compose exec backend curl -I https://picsum.photos/300/300

# Manually run photo script
docker compose exec backend python add_profile_photos.py
```

## 🎉 Success Verification

After successful initialization, you should see:

```
📊 Final Data Summary:
👥 Users: 4
🏢 Companies: 3
💼 Jobs: 3
📝 Posts: 44+
💬 Comments: 117+
🤝 Connections: 6
📸 Users with photos: 4/4
🖼️ Companies with logos: 3/3

🌐 Your LinkedIn Clone is ready!
```

## 📞 Support

If you encounter issues:
1. Check the logs with `docker compose logs backend -f`
2. Verify environment variables are set correctly
3. Try manual script execution for debugging
4. Use `--force` flag to recreate data if needed

Your LinkedIn Clone is now ready for development and testing! 🚀 