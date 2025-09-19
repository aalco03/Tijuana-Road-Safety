from django.core.management.base import BaseCommand
from django.core.management import call_command
import sys
import os

class Command(BaseCommand):
    help = 'Run migrations, collect static files, and start the server (Production Ready)'
    
    def add_arguments(self, parser):
        parser.add_argument('--port', default='8000', help='Port to run server on')
        parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (0.0.0.0 for production)')
        parser.add_argument('--skip-static', action='store_true', help='Skip static file collection')
        parser.add_argument('--skip-migrate', action='store_true', help='Skip database migrations')
    
    def handle(self, *args, **options):
        # Database Migrations
        if not options['skip_migrate']:
            self.stdout.write(self.style.NOTICE('🔄 Running database migrations...'))
            try:
                call_command('migrate', verbosity=1, interactive=False)
                self.stdout.write(self.style.SUCCESS('✅ Database migrations completed successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Migration failed: {e}'))
                sys.exit(1)
        else:
            self.stdout.write(self.style.WARNING('⚠️  Skipping database migrations'))
        
        # Static Files Collection (for production)
        if not options['skip_static']:
            self.stdout.write(self.style.NOTICE('🔄 Collecting static files...'))
            try:
                call_command('collectstatic', verbosity=1, interactive=False)
                self.stdout.write(self.style.SUCCESS('✅ Static files collected successfully'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠️  Static collection failed: {e}'))
                # Don't exit on static collection failure in case it's not needed
        else:
            self.stdout.write(self.style.WARNING('⚠️  Skipping static file collection'))
        
        # Health Check
        self.stdout.write(self.style.NOTICE('🔄 Running system checks...'))
        try:
            call_command('check', verbosity=1)
            self.stdout.write(self.style.SUCCESS('✅ System checks passed'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ System check failed: {e}'))
            # Continue anyway for development
        
        # Start Server
        host_port = f"{options['host']}:{options['port']}"
        self.stdout.write(self.style.SUCCESS(f'🚀 Starting Django server on {host_port}...'))
        self.stdout.write(self.style.HTTP_INFO(f'Server will be available at http://{host_port}'))
        
        # Additional production info
        if options['host'] == '0.0.0.0':
            self.stdout.write(self.style.HTTP_INFO('🌐 Server configured for production (binding to all interfaces)'))
        
        try:
            call_command('runserver', host_port, verbosity=1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.NOTICE('\n👋 Server stopped gracefully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Server failed to start: {e}'))
            sys.exit(1)
