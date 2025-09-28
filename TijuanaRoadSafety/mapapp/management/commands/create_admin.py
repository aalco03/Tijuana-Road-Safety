import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create admin user for production deployment'

    def handle(self, *args, **options):
        # Get credentials from environment variables for security
        admin_username = os.getenv('ADMIN_USERNAME', 'aalco03')
        admin_password = os.getenv('ADMIN_PASSWORD')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@tijuanaroadsafety.com')
        
        if not admin_password:
            self.stdout.write(
                self.style.ERROR('ADMIN_PASSWORD environment variable is required')
            )
            return
        
        # Check if admin user already exists
        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{admin_username}" already exists')
            )
            return
        
        # Create admin user
        admin_user = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin user: {admin_username}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Admin panel: https://your-domain.com/admin/')
        )
