#!/bin/bash

# Tijuana Road Safety - Production Startup Script
# This script handles automatic migrations and server startup

set -e  # Exit on any error

echo "🚀 Starting Tijuana Road Safety Application..."
echo "📅 $(date)"
echo "🌍 Environment: ${DJANGO_ENV:-production}"

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env"
    set -a  # automatically export all variables
    source .env
    set +a  # stop automatically exporting
fi

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    if [ -d "venv" ]; then
        echo "🔄 Activating virtual environment..."
        source venv/bin/activate
    fi
fi

# Check database connectivity
echo "🔍 Testing database connection..."
python manage.py dbshell --help > /dev/null 2>&1 || {
    echo "❌ Database connection test failed"
    exit 1
}

# Use our custom management command
echo "🎯 Using Django management command for startup..."
python manage.py migrate_and_run --host=0.0.0.0 --port=8000

echo "👋 Application shutdown complete"
