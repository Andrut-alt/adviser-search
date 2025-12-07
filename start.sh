#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo "-------- STARTING DEPLOYMENT SCRIPT --------"

echo "--> Applying database migrations..."
python manage.py migrate

echo "--> Collecting static files..."
python manage.py collectstatic --noinput

echo "--> Creating superuser (if needed)..."
python create_superuser.py

echo "--> Starting Gunicorn Server..."

gunicorn mentorion.wsgi:application