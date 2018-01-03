#!/bin/bash
set -e

if [ "$1" = '/opt/django-venv/bin/gunicorn' ]; then
    chown -R celery:celery /var/lib/celery
    /wait-for-it.sh postgres:5432
    /opt/django-venv/bin/python /opt/app/manage.py migrate --noinput
    /opt/django-venv/bin/python /opt/app/manage.py collectstatic --noinput
    exec "$@"
fi

exec "$@"
