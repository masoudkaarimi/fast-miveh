#!/bin/bash

# Wait for database to be ready
python manage.py migrate --noinput

# Load initial data
python manage.py load_data

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if not exists
python manage.py shell < create_superuser.py

# Start gunicorn
exec gunicorn -c core/gunicorn.py core.wsgi:application