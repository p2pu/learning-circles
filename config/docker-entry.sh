#!/bin/bash
set -e

./wait-for-it.sh postgres:5432

if [ "$1" = 'supervisord' ]; then
    chown -R celery:celery /var/lib/celery
    /opt/django-venv/bin/python /opt/app/manage.py migrate --noinput
    /opt/django-venv/bin/python /opt/app/manage.py collectstatic --noinput
    exec "$@"
fi

exec "$@"
