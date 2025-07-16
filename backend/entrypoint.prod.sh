#!/bin/sh

# Ensure the script fails on any error
set -e

# Wait for database to be ready
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"