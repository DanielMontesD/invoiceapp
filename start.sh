#!/bin/bash

# Create staticfiles directory
mkdir -p /app/staticfiles

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=invoicegen.settings_production

# Test basic Django setup
echo "Testing Django setup..."
python manage.py check --settings=invoicegen.settings_production

# Run migrations (only if database is available)
echo "Running migrations..."
python manage.py migrate --settings=invoicegen.settings_production || echo "Migrations failed, continuing..."

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn invoicegen.wsgi_production:application --bind 0.0.0.0:$PORT
