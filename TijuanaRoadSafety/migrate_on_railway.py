#!/usr/bin/env python
"""
Simple migration script for Railway deployment
This script will run migrations when executed on Railway
"""

import os
import sys
import subprocess

def main():
    print("🚀 Railway Migration Script")
    print("=" * 40)
    
    # Check if we're on Railway
    if not os.getenv('RAILWAY_ENVIRONMENT'):
        print("❌ This script should only run on Railway!")
        print("Current environment variables:")
        for key in ['DATABASE_URL', 'RAILWAY_ENVIRONMENT']:
            value = os.getenv(key)
            if value:
                print(f"  {key}: {value[:20]}..." if len(value) > 20 else f"  {key}: {value}")
            else:
                print(f"  {key}: Not set")
        return
    
    print("✅ Running on Railway environment")
    
    # Run migrations
    print("\n🔄 Running database migrations...")
    try:
        result = subprocess.run(['python', 'manage.py', 'migrate'], 
                              capture_output=True, text=True, check=True)
        print("✅ Migrations completed successfully!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        print(f"Error output: {e.stderr}")
        return
    
    # Show migration status
    print("\n📋 Migration status:")
    try:
        result = subprocess.run(['python', 'manage.py', 'showmigrations'], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Could not show migrations: {e}")
    
    # Create superuser if needed
    print("\n👤 Checking admin user...")
    create_user_script = '''
from django.contrib.auth.models import User
username = "aalco03"
if not User.objects.filter(username=username).exists():
    print("Creating admin user...")
else:
    print("Admin user already exists")
'''
    
    try:
        result = subprocess.run(['python', 'manage.py', 'shell'], 
                              input=create_user_script, text=True, 
                              capture_output=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not check admin user: {e}")
    
    print("\n🎉 Railway setup completed!")

if __name__ == "__main__":
    main()
