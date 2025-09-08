from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('report/', views.report_pothole, name = 'report_pothole'),
    path('report/<int:report_id>/', views.report_detail, name = 'report_detail'),
    path('report/<int:report_id>/audit/', views.audit_report, name = 'audit_report'),
    path('thank_you/', views.thank_you, name = 'thank_you'),
    path('whatsapp-webhook/', views.whatsapp_webhook, name = 'whatsapp-webhook'),
    path('api/check-nearby-potholes/', views.check_nearby_potholes, name='check_nearby_potholes'),
    path('api/increment-pothole-count/', views.increment_pothole_count, name='increment_pothole_count'),
]