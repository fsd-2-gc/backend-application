#!/usr/bin/env bash
set -e

if [ "${DJANGO_DEV:-0}" = "1" ]; then
  exec python manage.py runserver 0.0.0.0:8000
else
  exec gunicorn app.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3} --timeout 30
fi
