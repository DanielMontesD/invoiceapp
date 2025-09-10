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

# Start health check server (this will handle Railway's health checks)
echo "Starting health check server..."
exec python health.py
