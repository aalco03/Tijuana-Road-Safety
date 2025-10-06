#!/usr/bin/env python3
"""
Post-deployment script for Railway
Run this AFTER the app is deployed and has network access
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Railway Post-Deployment Setup")
    print("=" * 40)
    
    # Verify we're on Railway with database access
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL not found! Make sure this runs on Railway.")
        sys.exit(1)
    
    print("✅ DATABASE_URL found")
    
    # Run migrations
    if not run_command("python3 manage.py migrate", "Database migrations"):
        sys.exit(1)
    
    # Collect static files
    run_command("python3 manage.py collectstatic --noinput", "Static file collection")
    
    # Create admin user (safely)
    create_admin_script = '''
from django.contrib.auth.models import User
username = "aalco03"
password = "benedictismyFAVORITE16!*"
email = "admin@example.com"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"✅ Admin user '{username}' created")
else:
    print(f"ℹ️  Admin user '{username}' already exists")
'''
    
    print("\n🔄 Setting up admin user...")
    try:
        result = subprocess.run(['python3', 'manage.py', 'shell'], 
                              input=create_admin_script, text=True, 
                              capture_output=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Admin user setup failed: {e}")
    
    print("\n🎉 Post-deployment setup completed!")
    print("Your app should now be ready to accept submissions!")

if __name__ == "__main__":
    main()
