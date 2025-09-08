from django.db import models
import math

class PotholeReport(models.Model):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    severity = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='pothole_images/')
    timestamp = models.DateTimeField(auto_now_add=True)
    submission_count = models.IntegerField(default=1)
    approximate_address = models.CharField(max_length=255, blank=True, null=True)
    
    @classmethod
    def find_nearby_potholes(cls, latitude, longitude, radius_meters=50):
        """Find potholes within specified radius using Haversine formula"""
        # Convert radius from meters to degrees (approximate)
        radius_degrees = radius_meters / 111000  # 1 degree ≈ 111km
        
        nearby_potholes = []
        for pothole in cls.objects.all():
            distance = cls.calculate_distance(latitude, longitude, pothole.latitude, pothole.longitude)
            if distance <= radius_meters:
                nearby_potholes.append({
                    'pothole': pothole,
                    'distance': distance
                })
        
        return sorted(nearby_potholes, key=lambda x: x['distance'])
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon/2) * math.sin(delta_lon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c