# Generated migration for mobile/WhatsApp optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapapp', '0003_potholereport_approximate_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='potholereport',
            name='submission_source',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('web', 'Web Form'),
                    ('whatsapp', 'WhatsApp'),
                    ('api', 'API'),
                ],
                default='web',
                help_text='Source of the pothole report submission'
            ),
        ),
        migrations.AddField(
            model_name='potholereport',
            name='whatsapp_message_id',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                help_text='Twilio WhatsApp message ID for tracking'
            ),
        ),
        migrations.AddField(
            model_name='potholereport',
            name='ai_confidence_score',
            field=models.FloatField(
                blank=True,
                null=True,
                help_text='Roboflow AI confidence score for pothole detection'
            ),
        ),
        migrations.AddField(
            model_name='potholereport',
            name='status',
            field=models.CharField(
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
            ),
        ),
        migrations.AddField(
            model_name='potholereport',
            name='priority_level',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('low', 'Low'),
                    ('medium', 'Medium'),
                    ('high', 'High'),
                    ('urgent', 'Urgent'),
                ],
                default='medium',
                help_text='Priority level based on severity and location'
            ),
        ),
        migrations.AddField(
            model_name='potholereport',
            name='last_updated',
            field=models.DateTimeField(
                auto_now=True,
                help_text='Last time this report was updated'
            ),
        ),
        migrations.AddField(
            model_name='potholereport',
            name='reporter_name',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                help_text='Optional name of the person reporting'
            ),
        ),
        migrations.AddField(
            model_name='potholereport',
            name='additional_notes',
            field=models.TextField(
                blank=True,
                null=True,
                help_text='Additional notes or description from reporter'
            ),
        ),
        migrations.AlterField(
            model_name='potholereport',
            name='phone_number',
            field=models.CharField(
                max_length=20,
                blank=True,
                null=True,
                help_text='Phone number including country code (e.g., +52 for Mexico)'
            ),
        ),
    ]
