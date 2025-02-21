from django.db import models

class PotholeReport(models.Model):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    severity = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='pothole_images/')
    timestamp = models.DateTimeField(auto_now_add=True)