#!/bin/bash

# Create staticfiles directory
mkdir -p /app/staticfiles

# Collect static files
python manage.py collectstatic --noinput --settings=invoicegen.settings_production

# Start gunicorn
exec gunicorn invoicegen.wsgi_production:application --bind 0.0.0.0:$PORT
