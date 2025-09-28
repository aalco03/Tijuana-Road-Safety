import requests
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from mapapp.models import PotholeReport


class Command(BaseCommand):
    help = 'Populate approximate_address field for existing pothole reports using Google Geocoding API'

    def handle(self, *args, **options):
        # Get all reports without addresses
        reports_without_addresses = PotholeReport.objects.filter(
            approximate_address__isnull=True
        ) | PotholeReport.objects.filter(approximate_address='')
        
        total_reports = reports_without_addresses.count()
        self.stdout.write(f'Found {total_reports} reports without addresses')
        
        if total_reports == 0:
            self.stdout.write(self.style.SUCCESS('All reports already have addresses!'))
            return
        
        updated_count = 0
        
        for report in reports_without_addresses:
            try:
                # Use Google Geocoding API to get address
                url = f'https://maps.googleapis.com/maps/api/geocode/json'
                params = {
                    'latlng': f'{report.latitude},{report.longitude}',
                    'key': settings.GOOGLE_MAPS_API_KEY
                }
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if data['status'] == 'OK' and data['results']:
                    address = data['results'][0]['formatted_address']
                    report.approximate_address = address
                    report.save()
                    updated_count += 1
                    self.stdout.write(f'Updated report #{report.id}: {address}')
                else:
                    # Fallback to a generic address
                    report.approximate_address = f'Tijuana, BC, Mexico (Lat: {report.latitude:.4f}, Lng: {report.longitude:.4f})'
                    report.save()
                    updated_count += 1
                    self.stdout.write(f'Updated report #{report.id} with fallback address')
                
                # Add delay to respect API rate limits
                time.sleep(0.1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error updating report #{report.id}: {str(e)}')
                )
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} out of {total_reports} reports')
        )
