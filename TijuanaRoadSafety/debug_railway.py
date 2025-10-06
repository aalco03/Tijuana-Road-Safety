#!/usr/bin/env python
"""
Railway Database Diagnostic Script
This script helps diagnose database connectivity and migration issues on Railway
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TijuanaRoadSafety.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line
from mapapp.models import PotholeReport
from django.conf import settings

def test_database_connection():
    """Test basic database connectivity"""
    print("🔍 Testing Database Connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Database connected successfully!")
            print(f"   PostgreSQL Version: {version[0]}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_environment_variables():
    """Check critical environment variables"""
    print("\n🔍 Checking Environment Variables...")
    
    required_vars = [
        'DATABASE_URL',
        'DJANGO_SECRET_KEY',
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'API' in var or 'DATABASE_URL' in var:
                masked_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")

def check_migrations():
    """Check migration status"""
    print("\n🔍 Checking Migration Status...")
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print("❌ Unapplied migrations found:")
            for migration, backwards in plan:
                print(f"   - {migration}")
            return False
        else:
            print("✅ All migrations are applied")
            return True
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
        return False

def check_table_structure():
    """Check if the PotholeReport table exists and has correct structure"""
    print("\n🔍 Checking Table Structure...")
    try:
        with connection.cursor() as cursor:
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'mapapp_potholereport'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                print("❌ PotholeReport table does not exist")
                return False
            
            print("✅ PotholeReport table exists")
            
            # Check table columns
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'mapapp_potholereport'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            print("   Table columns:")
            expected_columns = [
                'id', 'phone_number', 'reporter_name', 'severity', 'latitude', 
                'longitude', 'image', 'approximate_address', 'additional_notes',
                'timestamp', 'last_updated', 'latest_submission_date', 
                'submission_count', 'submission_source', 'whatsapp_message_id',
                'ai_confidence_score', 'status', 'priority_level'
            ]
            
            found_columns = [col[0] for col in columns]
            
            for col in expected_columns:
                if col in found_columns:
                    print(f"   ✅ {col}")
                else:
                    print(f"   ❌ {col} (missing)")
            
            return True
            
    except Exception as e:
        print(f"❌ Error checking table structure: {e}")
        return False

def test_model_operations():
    """Test basic model operations"""
    print("\n🔍 Testing Model Operations...")
    try:
        # Test count
        count = PotholeReport.objects.count()
        print(f"✅ Current pothole reports count: {count}")
        
        # Test creating a test record (we'll delete it immediately)
        test_report = PotholeReport(
            severity=3,
            latitude=32.5149,
            longitude=-117.0382,
            approximate_address="Test Address, Tijuana",
            submission_source='api'
        )
        
        # Don't save the image field for this test
        print("✅ Model instantiation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Model operation failed: {e}")
        return False

def check_cloudinary_config():
    """Check Cloudinary configuration"""
    print("\n🔍 Checking Cloudinary Configuration...")
    try:
        import cloudinary
        print(f"✅ Cloudinary library imported")
        
        # Check if configuration is loaded
        if hasattr(settings, 'CLOUDINARY_STORAGE'):
            config = settings.CLOUDINARY_STORAGE
            if config.get('CLOUD_NAME'):
                print(f"✅ Cloudinary configured with cloud: {config['CLOUD_NAME']}")
                return True
            else:
                print("❌ Cloudinary cloud name not configured")
                return False
        else:
            print("❌ Cloudinary storage not configured")
            return False
            
    except ImportError:
        print("❌ Cloudinary library not available")
        return False
    except Exception as e:
        print(f"❌ Cloudinary check failed: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("🚀 Railway Database Diagnostic Tool")
    print("=" * 50)
    
    # Check if we're running on Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("✅ Running on Railway environment")
    else:
        print("⚠️  Not running on Railway (local environment)")
    
    results = []
    results.append(("Database Connection", test_database_connection()))
    results.append(("Environment Variables", check_environment_variables()))
    results.append(("Migrations", check_migrations()))
    results.append(("Table Structure", check_table_structure()))
    results.append(("Model Operations", test_model_operations()))
    results.append(("Cloudinary Config", check_cloudinary_config()))
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! The database should be working correctly.")
    else:
        print("\n⚠️  Some checks failed. Review the issues above.")
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("1. Run migrations: python manage.py migrate")
        print("2. Check Railway environment variables")
        print("3. Verify Cloudinary configuration")

if __name__ == "__main__":
    main()
