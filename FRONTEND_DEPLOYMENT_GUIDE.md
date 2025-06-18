# 🚀 Frontend Deployment Guide

## 📋 Overview
This guide will help you deploy the BYN frontend with your Railway backend.

**Your Railway Backend URL**: `https://byn.up.railway.app`

## 🔧 Environment Configuration

### Production Environment Variables
Copy these exact values to your frontend deployment platform:

```bash
REACT_APP_API_BASE_URL=https://byn.up.railway.app
REACT_APP_API_TIMEOUT=15000
REACT_APP_NAME=BYN - Build Your Network
REACT_APP_VERSION=1.0.0
REACT_APP_ENV=production
REACT_APP_DEBUG_API=false
```

## 🌐 Deployment Platforms

### Option 1: Vercel (Recommended)
1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy**:
   ```bash
   cd BYN/frontend
   vercel --prod
   ```

3. **Add Environment Variables** in Vercel Dashboard:
   - Go to your project → Settings → Environment Variables
   - Add each `REACT_APP_*` variable from above

### Option 2: Netlify
1. **Build the app**:
   ```bash
   cd BYN/frontend
   npm run build
   ```

2. **Deploy** via Netlify CLI or drag & drop the `build` folder

3. **Add Environment Variables** in Netlify Dashboard:
   - Go to Site Settings → Environment Variables
   - Add each `REACT_APP_*` variable from above

## 🛡️ Backend CORS Configuration

Your Railway backend needs to allow your frontend domain. Update your Railway environment variables:

```bash
# In Railway Dashboard → Variables
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,https://your-frontend-domain.netlify.app
ALLOWED_HOSTS=byn.up.railway.app,your-frontend-domain.vercel.app
```

## ✅ Deployment Checklist

### Before Deployment:
- [ ] Railway backend is running at `https://byn.up.railway.app`
- [ ] Test API endpoints: `https://byn.up.railway.app/api/auth/login/`
- [ ] Environment variables are configured
- [ ] Frontend builds successfully (`npm run build`)

### After Deployment:
- [ ] Test login/register functionality
- [ ] Check browser console for API errors
- [ ] Verify CORS is working (no CORS errors in console)
- [ ] Test all major features (jobs, companies, feed)

## 🔍 Testing Your Deployment

### Test API Connection
1. Open browser console on your deployed frontend
2. Run this in console:
```javascript
fetch('https://byn.up.railway.app/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'test@test.com', password: 'test' })
})
.then(r => console.log('Status:', r.status))
.catch(e => console.error('Error:', e))
```

### Common Issues & Solutions

**CORS Error**:
```
Access to fetch at 'https://byn.up.railway.app/api/' from origin 'https://yourapp.vercel.app' has been blocked by CORS policy
```
**Solution**: Add your frontend domain to Railway's `CORS_ALLOWED_ORIGINS`

**API Timeout**:
```
Error: timeout of 15000ms exceeded
```
**Solution**: Railway might be sleeping. First request takes ~30 seconds to wake up.

**401 Unauthorized**:
```
Response status: 401
```
**Solution**: Check if authentication endpoints are working correctly.

## 📞 Support

If you encounter issues:
1. Check Railway logs for backend errors
2. Check browser console for frontend errors
3. Verify environment variables are set correctly
4. Test API endpoints directly with Postman

## 🎯 Next Steps

After successful deployment:
1. Set up custom domain (optional)
2. Configure analytics (Google Analytics, etc.)
3. Set up monitoring (Sentry, etc.)
4. Configure CDN for better performance 