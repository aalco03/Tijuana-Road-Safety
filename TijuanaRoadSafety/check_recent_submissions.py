#!/usr/bin/env python
"""
Check recent submissions and their image URLs
"""

import os
import sys
import django
from pathlib import Path

# Set up Django environment with public database URL
os.environ['DATABASE_URL'] = "postgresql://postgres:LEMVRxQsPttEMwHCSpiZtBQIfRlZxFrT@maglev.proxy.rlwy.net:13086/railway"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TijuanaRoadSafety.settings')
django.setup()

from mapapp.models import PotholeReport
from django.utils import timezone
from datetime import timedelta

def check_recent_submissions():
    """Check submissions from the last hour"""
    print("🔍 Checking Recent Submissions...")
    
    # Get submissions from last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_reports = PotholeReport.objects.filter(timestamp__gte=one_hour_ago).order_by('-timestamp')
    
    print(f"Found {recent_reports.count()} submissions in the last hour")
    
    for report in recent_reports:
        print(f"\n📋 Report #{report.id} (submitted {report.timestamp}):")
        print(f"   Severity: {report.severity}")
        print(f"   Location: {report.latitude}, {report.longitude}")
        print(f"   Source: {report.submission_source}")
        print(f"   Has image: {'Yes' if report.image else 'No'}")
        
        if report.image:
            print(f"   Image name: {report.image.name}")
            print(f"   Image URL: {report.image.url}")
            
            if 'cloudinary.com' in report.image.url:
                print("   ✅ Cloudinary URL - should work!")
            else:
                print("   ❌ Not a Cloudinary URL")
        else:
            print("   ❌ No image attached")

def main():
    print("🚀 Recent Submissions Check")
    print("=" * 50)
    
    try:
        check_recent_submissions()
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Next steps:")
    print("1. Submit a new pothole report through the web form")
    print("2. Run this script again to see if it appears")
    print("3. Check if the image URL contains 'cloudinary.com'")

if __name__ == "__main__":
    main()
