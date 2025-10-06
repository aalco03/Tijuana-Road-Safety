#!/usr/bin/env python
"""
Test script to verify pothole submission functionality
"""

import os
import sys
import django
from pathlib import Path
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TijuanaRoadSafety.settings')
django.setup()

from mapapp.models import PotholeReport
from mapapp.forms import PotholeReportForm

def create_test_image():
    """Create a simple test image"""
    # Create a simple red square image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return SimpleUploadedFile(
        name='test_pothole.jpg',
        content=img_bytes.getvalue(),
        content_type='image/jpeg'
    )

def test_database_connection():
    """Test basic database operations"""
    print("🔍 Testing database connection...")
    try:
        count = PotholeReport.objects.count()
        print(f"✅ Database connected. Current reports: {count}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_model_creation():
    """Test creating a PotholeReport directly"""
    print("\n🔍 Testing direct model creation...")
    try:
        # Create test image
        test_image = create_test_image()
        
        # Create report
        report = PotholeReport.objects.create(
            severity=3,
            latitude=32.5149,
            longitude=-117.0382,
            image=test_image,
            approximate_address="Test Street, Tijuana",
            submission_source='api',
            additional_notes="Test submission from script"
        )
        
        print(f"✅ Model created successfully with ID: {report.id}")
        
        # Clean up - delete the test report
        report.delete()
        print("✅ Test report cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_form_validation():
    """Test form validation and saving"""
    print("\n🔍 Testing form validation...")
    try:
        # Create test image
        test_image = create_test_image()
        
        # Test form data
        form_data = {
            'severity': 4,
            'latitude': 32.5149,
            'longitude': -117.0382,
            'approximate_address': 'Test Form Street, Tijuana',
            'additional_notes': 'Test form submission'
        }
        
        form_files = {
            'image': test_image
        }
        
        form = PotholeReportForm(form_data, form_files)
        
        if form.is_valid():
            saved_report = form.save()
            print(f"✅ Form validation and save successful. Report ID: {saved_report.id}")
            
            # Verify the report was saved correctly
            retrieved_report = PotholeReport.objects.get(id=saved_report.id)
            print(f"✅ Report retrieved successfully: {retrieved_report}")
            
            # Clean up
            retrieved_report.delete()
            print("✅ Test report cleaned up")
            return True
        else:
            print(f"❌ Form validation failed: {form.errors}")
            return False
            
    except Exception as e:
        print(f"❌ Form test failed: {e}")
        return False

def test_cloudinary_config():
    """Test Cloudinary configuration"""
    print("\n🔍 Testing Cloudinary configuration...")
    try:
        from django.conf import settings
        
        if hasattr(settings, 'CLOUDINARY_STORAGE'):
            config = settings.CLOUDINARY_STORAGE
            cloud_name = config.get('CLOUD_NAME')
            api_key = config.get('API_KEY')
            
            if cloud_name and api_key:
                print(f"✅ Cloudinary configured: {cloud_name}")
                return True
            else:
                print("❌ Cloudinary configuration incomplete")
                return False
        else:
            print("❌ Cloudinary not configured")
            return False
            
    except Exception as e:
        print(f"❌ Cloudinary test failed: {e}")
        return False

def main():
    print("🚀 Pothole Submission Test Suite")
    print("=" * 50)
    
    # Check environment
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("✅ Running on Railway")
    else:
        print("⚠️  Running locally")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Direct Model Creation", test_model_creation),
        ("Form Validation", test_form_validation),
        ("Cloudinary Configuration", test_cloudinary_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Submission functionality should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("1. Ensure all migrations are applied: python manage.py migrate")
        print("2. Check environment variables are set correctly")
        print("3. Verify Cloudinary configuration")
        print("4. Check Railway logs for detailed error messages")

if __name__ == "__main__":
    main()
