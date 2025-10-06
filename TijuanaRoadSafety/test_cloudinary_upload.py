#!/usr/bin/env python
"""
Test Cloudinary upload directly on Railway
"""

import os
import sys
import django
from pathlib import Path

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TijuanaRoadSafety.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from mapapp.models import PotholeReport
from PIL import Image
import io

def test_direct_cloudinary_upload():
    """Test uploading directly to Cloudinary"""
    print("🧪 Testing Direct Cloudinary Upload...")
    
    try:
        # Create a test image
        img = Image.new('RGB', (200, 200), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        test_image = SimpleUploadedFile(
            name='cloudinary_test.jpg',
            content=img_bytes.getvalue(),
            content_type='image/jpeg'
        )
        
        print("✅ Test image created")
        
        # Create a test report
        test_report = PotholeReport.objects.create(
            severity=4,
            latitude=32.5149,
            longitude=-117.0382,
            image=test_image,
            approximate_address="Cloudinary Test Street, Tijuana",
            submission_source='api',
            additional_notes="Direct Cloudinary upload test"
        )
        
        print(f"✅ Test report created with ID: {test_report.id}")
        
        # Check the image URL
        if test_report.image:
            image_url = test_report.image.url
            print(f"📷 Image URL: {image_url}")
            
            if 'cloudinary.com' in image_url:
                print("✅ SUCCESS: Image uploaded to Cloudinary!")
                print(f"   Full URL: {image_url}")
            elif image_url.startswith('/media/'):
                print("❌ PROBLEM: Image stored locally, not Cloudinary")
                print("   This means Cloudinary configuration isn't working")
            else:
                print(f"❓ Unknown URL format: {image_url}")
        else:
            print("❌ No image attached to report")
        
        # Don't delete - let's keep it for testing
        print(f"🔍 Test report kept for inspection (ID: {test_report.id})")
        
        return test_report
        
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_django_settings():
    """Check Django settings for Cloudinary"""
    print("\n🔧 Checking Django Settings...")
    
    from django.conf import settings
    
    # Check DEFAULT_FILE_STORAGE
    storage = getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')
    print(f"DEFAULT_FILE_STORAGE: {storage}")
    
    if 'cloudinary' in storage.lower():
        print("✅ Using Cloudinary storage")
    else:
        print("❌ NOT using Cloudinary storage")
    
    # Check CLOUDINARY_STORAGE
    if hasattr(settings, 'CLOUDINARY_STORAGE'):
        config = settings.CLOUDINARY_STORAGE
        print(f"CLOUDINARY_STORAGE: {config}")
        
        cloud_name = config.get('CLOUD_NAME')
        if cloud_name:
            print(f"✅ Cloud Name: {cloud_name}")
        else:
            print("❌ Cloud Name not set")
    else:
        print("❌ CLOUDINARY_STORAGE not configured")

def main():
    print("🚀 Cloudinary Upload Test")
    print("=" * 50)
    
    check_django_settings()
    test_report = test_direct_cloudinary_upload()
    
    print("\n" + "=" * 50)
    if test_report and test_report.image and 'cloudinary.com' in test_report.image.url:
        print("🎉 SUCCESS: Cloudinary is working!")
        print("New submissions should now upload images to Cloudinary.")
    else:
        print("❌ PROBLEM: Images are not uploading to Cloudinary")
        print("Need to fix the configuration.")

if __name__ == "__main__":
    main()
