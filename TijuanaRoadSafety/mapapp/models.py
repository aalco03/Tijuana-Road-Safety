from django.db import models
import math

class PotholeReport(models.Model):
    # Contact Information
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text='Phone number including country code (e.g., +52 for Mexico)'
    )
    reporter_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Optional name of the person reporting'
    )
    
    # Core Report Data
    severity = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='pothole_images/')
    approximate_address = models.CharField(max_length=255, blank=True, null=True)
    additional_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes or description from reporter'
    )
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text='Last time this report was updated'
    )
    
    # Tracking & Analytics
    submission_count = models.IntegerField(default=1)
    submission_source = models.CharField(
        max_length=20,
        choices=[
            ('web', 'Web Form'),
            ('whatsapp', 'WhatsApp'),
            ('api', 'API'),
        ],
        default='web',
        help_text='Source of the pothole report submission'
    )
    whatsapp_message_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Twilio WhatsApp message ID for tracking'
    )
    ai_confidence_score = models.FloatField(
        blank=True,
        null=True,
        help_text='Roboflow AI confidence score for pothole detection'
    )
    
    # Status Management
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Review'),
            ('verified', 'Verified'),
            ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'),
            ('duplicate', 'Duplicate'),
            ('invalid', 'Invalid'),
        ],
        default='pending',
        help_text='Current status of the pothole report'
    )
    priority_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='medium',
        help_text='Priority level based on severity and location'
    )
    
    def save(self, *args, **kwargs):
        """Override save to set priority level based on severity and AI confidence"""
        # Auto-set priority based on severity
        if self.severity >= 4:
            self.priority_level = 'high'
        elif self.severity >= 3:
            self.priority_level = 'medium'
        else:
            self.priority_level = 'low'
            
        # Upgrade to urgent if AI confidence is very high and severity is high
        if self.ai_confidence_score and self.ai_confidence_score >= 0.9 and self.severity >= 4:
            self.priority_level = 'urgent'
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Pothole Report #{self.id} - {self.get_status_display()} ({self.get_priority_level_display()})"
    
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