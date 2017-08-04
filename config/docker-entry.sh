#!/bin/bash
set -e

if [ "$1" = 'supervisord' ]; then
    /wait-for-it.sh postgres:5432
    chown -R celery:celery /var/lib/celery
    /opt/django-venv/bin/python /opt/app/manage.py migrate --noinput
    /opt/django-venv/bin/python /opt/app/manage.py collectstatic --noinput
    exec "$@"
fi

exec "$@"
