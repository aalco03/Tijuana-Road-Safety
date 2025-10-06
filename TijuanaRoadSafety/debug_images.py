#!/usr/bin/env python
"""
Debug script to check image storage and URLs
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

from mapapp.models import PotholeReport
from django.conf import settings

def check_cloudinary_config():
    """Check Cloudinary configuration"""
    print("🔍 Checking Cloudinary Configuration...")
    
    # Check environment variables
    cloudinary_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
    for var in cloudinary_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:10]}...")
        else:
            print(f"❌ {var}: Not set")
    
    # Check Django settings
    if hasattr(settings, 'CLOUDINARY_STORAGE'):
        config = settings.CLOUDINARY_STORAGE
        print(f"✅ CLOUDINARY_STORAGE configured")
        print(f"   Cloud Name: {config.get('CLOUD_NAME', 'Not set')}")
    else:
        print("❌ CLOUDINARY_STORAGE not configured")
    
    # Check file storage setting
    if hasattr(settings, 'DEFAULT_FILE_STORAGE'):
        print(f"✅ DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    else:
        print("❌ DEFAULT_FILE_STORAGE not set")

def check_existing_reports():
    """Check existing pothole reports and their images"""
    print("\n🔍 Checking Existing Reports...")
    
    reports = PotholeReport.objects.all()
    print(f"Total reports: {reports.count()}")
    
    for report in reports[:5]:  # Check first 5 reports
        print(f"\n📋 Report #{report.id}:")
        print(f"   Has image: {'Yes' if report.image else 'No'}")
        
        if report.image:
            print(f"   Image name: {report.image.name}")
            print(f"   Image URL: {report.image.url}")
            print(f"   Image path: {getattr(report.image, 'path', 'N/A (Cloudinary)')}")
            
            # Try to get the actual URL
            try:
                actual_url = str(report.image.url)
                print(f"   Actual URL: {actual_url}")
                
                # Check if it's a Cloudinary URL
                if 'cloudinary.com' in actual_url:
                    print("   ✅ Using Cloudinary")
                elif actual_url.startswith('/media/'):
                    print("   ⚠️  Using local media (not Cloudinary)")
                else:
                    print(f"   ❓ Unknown storage type: {actual_url}")
                    
            except Exception as e:
                print(f"   ❌ Error getting URL: {e}")

def test_image_upload():
    """Test creating a report with an image"""
    print("\n🔍 Testing Image Upload...")
    
    try:
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        test_image = SimpleUploadedFile(
            name='test_debug.jpg',
            content=img_bytes.getvalue(),
            content_type='image/jpeg'
        )
        
        # Create a test report
        test_report = PotholeReport.objects.create(
            severity=3,
            latitude=32.5149,
            longitude=-117.0382,
            image=test_image,
            approximate_address="Debug Test Street, Tijuana",
            submission_source='api',
            additional_notes="Debug test submission"
        )
        
        print(f"✅ Test report created with ID: {test_report.id}")
        print(f"   Image URL: {test_report.image.url}")
        
        # Check if URL is accessible
        if 'cloudinary.com' in test_report.image.url:
            print("   ✅ Image uploaded to Cloudinary")
        else:
            print("   ⚠️  Image not on Cloudinary")
        
        # Clean up
        test_report.delete()
        print("   ✅ Test report cleaned up")
        
    except Exception as e:
        print(f"   ❌ Image upload test failed: {e}")

def main():
    print("🚀 Image Debug Tool")
    print("=" * 50)
    
    check_cloudinary_config()
    check_existing_reports()
    test_image_upload()
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDATIONS:")
    print("1. Check that Cloudinary environment variables are set in Railway")
    print("2. Verify images are being uploaded to Cloudinary (URLs should contain 'cloudinary.com')")
    print("3. Check browser developer tools for image loading errors")
    print("4. Test submitting a new pothole report to see if images work")

if __name__ == "__main__":
    main()
