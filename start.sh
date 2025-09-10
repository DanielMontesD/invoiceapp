#!/bin/bash

# Create staticfiles directory
mkdir -p /app/staticfiles

# Collect static files
python manage.py collectstatic --noinput --settings=invoicegen.settings_production

# Test database connection
echo "Testing database connection..."
python manage.py check --settings=invoicegen.settings_production

# Run migrations
echo "Running migrations..."
python manage.py migrate --settings=invoicegen.settings_production

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn invoicegen.wsgi_production:application --bind 0.0.0.0:$PORT
