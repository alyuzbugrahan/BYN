# 🚀 Railway Deployment Guide - BYN LinkedIn Clone

## 📋 Pre-Deployment Checklist

✅ **Backend Ready:**
- ✅ Django settings optimized for Railway
- ✅ DATABASE_URL support added with `dj-database-url`
- ✅ Railway.json configuration file created
- ✅ Requirements.txt optimized (13 essential packages)
- ✅ Procfile created for Railway compatibility
- ✅ Health check endpoint: `/api/`
- ✅ Demo users management command ready
- ✅ WhiteNoise configured for static files
- ✅ CORS configured for Railway + Vercel

---

## 🚂 Railway Deployment Steps

### 1. **Create Railway Project**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway new
```

### 2. **Connect GitHub Repository**
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your BYN repository
5. Select the `backend` folder as the root directory

### 3. **Add PostgreSQL Database**
1. In Railway dashboard, click "Add Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create DATABASE_URL environment variable

### 4. **Configure Environment Variables**
In Railway Dashboard → Variables, add:

```bash
# Required Variables
SECRET_KEY=your-very-secure-secret-key-here-minimum-50-characters-long
DEBUG=False
ENVIRONMENT=production

# Domain Configuration (update after deployment)
ALLOWED_HOSTS=your-app-name.railway.app,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,https://your-app-name.railway.app

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True

# Optional: Admin User
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your-strong-admin-password
```

### 5. **Deploy the Application**
1. Railway will automatically deploy when you push to main branch
2. Monitor deployment in Railway Dashboard → Deployments
3. Check logs for any issues

### 6. **Post-Deployment Setup**

#### Create Demo Users:
```bash
# Using Railway CLI
railway run python manage.py create_production_users

# Or via Railway Dashboard → Console
python manage.py create_production_users
```

#### Create Admin User (if not done via environment):
```bash
railway run python manage.py createsuperuser
```

#### Load Sample Data (optional):
```bash
railway run python manage.py create_sample_feed_data
```

---

## 🔗 Frontend Configuration

### Update Vercel Frontend
Update your Vercel environment variables:

```bash
# In Vercel Dashboard → Settings → Environment Variables
REACT_APP_API_URL=https://your-app-name.railway.app
REACT_APP_BACKEND_URL=https://your-app-name.railway.app
```

### Update CORS in Backend
After getting your Railway URL, update the CORS_ALLOWED_ORIGINS in Railway variables:
```bash
CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,https://your-app-name.railway.app
```

---

## 🧪 Testing Deployment

### 1. **Health Check**
```bash
curl https://your-app-name.railway.app/api/
```
Expected response:
```json
{
  "status": "healthy",
  "service": "BYN Backend API",
  "message": "Build Your Network is running successfully!"
}
```

### 2. **Authentication Test**
```bash
curl -X POST https://your-app-name.railway.app/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test1234!"}'
```

### 3. **Admin Panel**
Visit: `https://your-app-name.railway.app/admin/`

### 4. **API Documentation**
Visit: `https://your-app-name.railway.app/api/docs/`

---

## 🔧 Troubleshooting

### Common Issues:

**1. Database Connection Error:**
- Ensure PostgreSQL service is running
- Check DATABASE_URL is automatically set by Railway

**2. Static Files Not Loading:**
- Run: `railway run python manage.py collectstatic --noinput`
- Verify WhiteNoise is in MIDDLEWARE

**3. CORS Errors:**
- Update CORS_ALLOWED_ORIGINS with correct domains
- Ensure both frontend and backend URLs are included

**4. 500 Internal Server Error:**
- Check Railway logs in Dashboard → Deployments
- Verify all environment variables are set
- Check SECRET_KEY is set and secure

### Debug Commands:
```bash
# Check logs
railway logs

# Run Django commands
railway run python manage.py check
railway run python manage.py migrate --run-syncdb

# SSH into container
railway shell
```

---

## 📊 Production Monitoring

### Environment Variables to Monitor:
- `DEBUG=False` (never True in production)
- `SECRET_KEY` (must be secure, 50+ characters)
- `DATABASE_URL` (automatically provided by Railway)
- `ALLOWED_HOSTS` (your Railway domain)

### Performance Settings:
- Gunicorn workers: 4 (configured in railway.json)
- Request timeout: 120 seconds
- Health check: `/api/` endpoint

---

## 🎯 Demo Credentials

After deployment, these demo accounts will be available:

| Email | Password | Role |
|-------|----------|------|
| `test@example.com` | `Test1234!` | Demo User |
| `john.doe@example.com` | `testpass123` | Software Engineer |
| `jane.smith@example.com` | `testpass123` | Product Manager |
| `mike.wilson@example.com` | `testpass123` | Data Scientist |

---

## ✅ Success Checklist

- [ ] Railway project created and deployed
- [ ] PostgreSQL database connected
- [ ] Environment variables configured
- [ ] Demo users created
- [ ] Frontend connected to Railway backend
- [ ] CORS configured correctly
- [ ] Health check endpoint responding
- [ ] Admin panel accessible
- [ ] API documentation available

Your BYN LinkedIn Clone is now live on Railway! 🎉 