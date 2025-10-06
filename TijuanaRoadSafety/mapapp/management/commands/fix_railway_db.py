from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from mapapp.models import PotholeReport
import os

class Command(BaseCommand):
    help = 'Fix Railway database issues and ensure proper setup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('🚀 Railway Database Fix Tool'))
        self.stdout.write('=' * 50)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Step 1: Check database connection
        self.stdout.write('\n1. Testing database connection...')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                self.stdout.write(self.style.SUCCESS(f'   ✅ Connected to PostgreSQL: {version[0][:50]}...'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Database connection failed: {e}'))
            return
        
        # Step 2: Run migrations
        self.stdout.write('\n2. Applying migrations...')
        if not dry_run:
            try:
                call_command('migrate', verbosity=1)
                self.stdout.write(self.style.SUCCESS('   ✅ Migrations applied successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Migration failed: {e}'))
                return
        else:
            self.stdout.write('   📋 Would run: python manage.py migrate')
        
        # Step 3: Check table structure
        self.stdout.write('\n3. Verifying table structure...')
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns
                    WHERE table_name = 'mapapp_potholereport'
                    ORDER BY ordinal_position;
                """)
                columns = [row[0] for row in cursor.fetchall()]
                
                required_columns = [
                    'id', 'severity', 'latitude', 'longitude', 'image',
                    'timestamp', 'submission_count', 'latest_submission_date'
                ]
                
                missing_columns = [col for col in required_columns if col not in columns]
                
                if missing_columns:
                    self.stdout.write(self.style.ERROR(f'   ❌ Missing columns: {missing_columns}'))
                else:
                    self.stdout.write(self.style.SUCCESS('   ✅ All required columns present'))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Table check failed: {e}'))
        
        # Step 4: Test model operations
        self.stdout.write('\n4. Testing model operations...')
        try:
            count = PotholeReport.objects.count()
            self.stdout.write(self.style.SUCCESS(f'   ✅ Current reports: {count}'))
            
            # Test if we can query the model
            recent_reports = PotholeReport.objects.order_by('-timestamp')[:5]
            self.stdout.write(self.style.SUCCESS(f'   ✅ Can query recent reports: {len(recent_reports)} found'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Model operations failed: {e}'))
        
        # Step 5: Fix any data inconsistencies
        self.stdout.write('\n5. Fixing data inconsistencies...')
        if not dry_run:
            try:
                # Update any reports missing latest_submission_date
                reports_to_fix = PotholeReport.objects.filter(latest_submission_date__isnull=True)
                count_fixed = 0
                
                for report in reports_to_fix:
                    report.latest_submission_date = report.timestamp
                    report.save()
                    count_fixed += 1
                
                if count_fixed > 0:
                    self.stdout.write(self.style.SUCCESS(f'   ✅ Fixed {count_fixed} reports missing latest_submission_date'))
                else:
                    self.stdout.write(self.style.SUCCESS('   ✅ No data inconsistencies found'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Data fix failed: {e}'))
        else:
            try:
                count_to_fix = PotholeReport.objects.filter(latest_submission_date__isnull=True).count()
                self.stdout.write(f'   📋 Would fix {count_to_fix} reports missing latest_submission_date')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Could not check data: {e}'))
        
        # Step 6: Verify Cloudinary setup
        self.stdout.write('\n6. Checking Cloudinary configuration...')
        cloudinary_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
        cloudinary_ok = all(os.getenv(var) for var in cloudinary_vars)
        
        if cloudinary_ok:
            self.stdout.write(self.style.SUCCESS('   ✅ Cloudinary environment variables configured'))
        else:
            missing_vars = [var for var in cloudinary_vars if not os.getenv(var)]
            self.stdout.write(self.style.ERROR(f'   ❌ Missing Cloudinary variables: {missing_vars}'))
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('🎉 Railway database fix completed!'))
        
        if not dry_run:
            self.stdout.write('\n📝 NEXT STEPS:')
            self.stdout.write('1. Test submitting a pothole report through the web form')
            self.stdout.write('2. Check the admin panel to verify data is being saved')
            self.stdout.write('3. Monitor Railway logs for any errors')
        else:
            self.stdout.write('\n📝 To apply changes, run: python manage.py fix_railway_db')
