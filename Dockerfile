FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY TijuanaRoadSafety/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY TijuanaRoadSafety/ /app/

# Collect static files (safe to do during build)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start command
CMD ["gunicorn", "TijuanaRoadSafety.wsgi:application", "--bind", "0.0.0.0:8000"]
