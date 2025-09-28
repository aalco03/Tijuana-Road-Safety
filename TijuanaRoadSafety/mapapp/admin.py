from django.contrib import admin
from django.utils.html import format_html
from .models import PotholeReport

# Register your models here.

@admin.register(PotholeReport)
class PotholeReportAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'image_thumbnail', 
        'get_street_name', 
        'severity', 
        'submission_count',
        'status',
        'priority_level',
        'timestamp',
        'latest_submission_date'
    ]
    
    list_filter = [
        'severity', 
        'status', 
        'priority_level', 
        'submission_source',
        'timestamp'
    ]
    
    search_fields = [
        'phone_number', 
        'approximate_address', 
        'additional_notes'
    ]
    
    readonly_fields = [
        'image_preview', 
        'timestamp', 
        'last_updated',
        'submission_count',
        'latest_submission_date'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('image_preview', 'severity', 'status', 'priority_level')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'approximate_address')
        }),
        ('Contact & Notes', {
            'fields': ('phone_number', 'reporter_name', 'additional_notes')
        }),
        ('Tracking', {
            'fields': ('submission_count', 'submission_source', 'timestamp', 'last_updated', 'latest_submission_date'),
            'classes': ('collapse',)
        }),
        ('AI Analysis', {
            'fields': ('ai_confidence_score',),
            'classes': ('collapse',)
        })
    )
    
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    image_thumbnail.short_description = "Image"
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: contain;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = "Image Preview"
    
    # Enable bulk actions
    actions = ['mark_as_resolved', 'mark_as_in_progress', 'export_as_csv']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved')
        self.message_user(request, f"{queryset.count()} reports marked as resolved.")
    mark_as_resolved.short_description = "Mark selected reports as resolved"
    
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        self.message_user(request, f"{queryset.count()} reports marked as in progress.")
    mark_as_in_progress.short_description = "Mark selected reports as in progress"
