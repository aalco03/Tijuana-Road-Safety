# Railway Deployment Troubleshooting Guide

## Issue: Submissions Not Being Stored

This guide helps diagnose and fix issues with pothole submissions not being stored in the Railway PostgreSQL database.

## Quick Fix Commands

Run these commands on Railway to diagnose and fix the issue:

### 1. Run Database Diagnostics
```bash
python debug_railway.py
```

### 2. Apply Database Fixes
```bash
python manage.py fix_railway_db
```

### 3. Test Submission Functionality
```bash
python test_submission.py
```

### 4. Run Full Deployment Script
```bash
python railway_deploy.py
```

## Manual Steps

If the automated scripts don't work, follow these manual steps:

### Step 1: Check Environment Variables
Ensure these environment variables are set in Railway:

- `DATABASE_URL` - PostgreSQL connection string (auto-set by Railway)
- `DJANGO_SECRET_KEY` - Django secret key
- `CLOUDINARY_CLOUD_NAME` - Cloudinary cloud name
- `CLOUDINARY_API_KEY` - Cloudinary API key  
- `CLOUDINARY_API_SECRET` - Cloudinary API secret
- `GOOGLE_MAPS_API_KEY` - Google Maps API key (optional)
- `ROBOFLOW_API_KEY` - Roboflow API key (optional)

### Step 2: Apply Database Migrations
```bash
python manage.py migrate
```

### Step 3: Create Admin User
```bash
python manage.py createsuperuser
```

### Step 4: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

## Common Issues and Solutions

### Issue 1: Migrations Not Applied
**Symptoms:** Database schema errors, missing columns
**Solution:** Run `python manage.py migrate`

### Issue 2: Cloudinary Not Configured
**Symptoms:** Image upload failures, file storage errors
**Solution:** Set Cloudinary environment variables in Railway

### Issue 3: Database Connection Issues
**Symptoms:** Connection refused, database errors
**Solution:** Check Railway PostgreSQL service is running and DATABASE_URL is set

### Issue 4: Debug Mode in Production
**Symptoms:** Security warnings, verbose error pages
**Solution:** Set `DEBUG=False` environment variable in Railway

## Verification Steps

After applying fixes:

1. **Test Web Form:** Submit a pothole report through the web interface
2. **Check Admin Panel:** Visit `/admin/` and verify reports are saved
3. **Check Logs:** Monitor Railway deployment logs for errors
4. **Test API Endpoints:** Verify `/check_nearby_potholes/` works

## Database Schema

The PotholeReport model should have these fields:
- `id` (Primary Key)
- `severity` (Integer 1-5)
- `latitude` (Float)
- `longitude` (Float)
- `image` (ImageField - stored in Cloudinary)
- `approximate_address` (CharField)
- `timestamp` (DateTimeField)
- `latest_submission_date` (DateTimeField)
- `submission_count` (Integer)
- `submission_source` (CharField)
- `status` (CharField)
- `priority_level` (CharField)

## Logging

The application now includes comprehensive logging. Check Railway logs for:
- Form validation errors
- Database save operations
- Image processing steps
- AI detection results

## Contact

If issues persist after following this guide, check:
1. Railway deployment logs
2. PostgreSQL service status
3. Cloudinary dashboard for upload errors

## Files Added/Modified

- `debug_railway.py` - Database diagnostic tool
- `railway_deploy.py` - Automated deployment script
- `test_submission.py` - Submission functionality test
- `mapapp/management/commands/fix_railway_db.py` - Database fix command
- `settings.py` - Added logging configuration
- `views.py` - Added comprehensive logging
