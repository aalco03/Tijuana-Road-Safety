#!/usr/bin/env python
"""
Railway Deployment and Database Fix Script
Run this script on Railway to diagnose and fix database issues
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ Success!")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Failed with exit code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    print("🚀 Railway Database Deployment Script")
    print("=" * 50)
    
    # Check if we're on Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("✅ Running on Railway environment")
    else:
        print("⚠️  Not on Railway - this script is designed for Railway deployment")
    
    # Step 1: Install dependencies (in case they're missing)
    print("\n1️⃣ Installing dependencies...")
    run_command("pip install -r requirements.txt", "Installing Python packages")
    
    # Step 2: Collect static files
    print("\n2️⃣ Collecting static files...")
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    # Step 3: Run migrations
    print("\n3️⃣ Running database migrations...")
    run_command("python manage.py migrate", "Applying database migrations")
    
    # Step 4: Create superuser if it doesn't exist
    print("\n4️⃣ Creating admin user...")
    create_superuser_script = '''
from django.contrib.auth.models import User
import os

username = "aalco03"
password = "benedictismyFAVORITE16!*"
email = "admin@roadsafety.com"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser {username} created successfully")
else:
    print(f"Superuser {username} already exists")
'''
    
    with open('create_admin.py', 'w') as f:
        f.write(create_superuser_script)
    
    run_command("python manage.py shell < create_admin.py", "Creating admin user")
    
    # Step 5: Run diagnostic script
    print("\n5️⃣ Running database diagnostics...")
    run_command("python debug_railway.py", "Running database diagnostics")
    
    # Step 6: Run the database fix command
    print("\n6️⃣ Running database fixes...")
    run_command("python manage.py fix_railway_db", "Fixing database issues")
    
    print("\n" + "=" * 50)
    print("🎉 Railway deployment completed!")
    print("\n📝 NEXT STEPS:")
    print("1. Check the Railway logs for any errors")
    print("2. Test the web application URL")
    print("3. Try submitting a pothole report")
    print("4. Check the admin panel at /admin/")

if __name__ == "__main__":
    main()
