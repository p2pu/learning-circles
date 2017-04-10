FROM ubuntu:14.04

# Install requirements
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    python \
    python-dev \
    python-distribute \
    python-pip \
    python-virtualenv \
    supervisor

# Setup application
COPY requirements.txt /var/app/
RUN virtualenv /var/django-venv && /var/django-venv/bin/pip install -r /var/app/requirements.txt
COPY . /var/app/
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY config/docker-entry.sh /docker-entry.sh
RUN mkdir -p /var/lib/celery && useradd celery && chown celery:celery /var/lib/celery/

ENV DATABASE_URL="sqlite:////var/app/db.sqlite3" \
    ADMIN_EMAIL="" \
    SECRET_KEY="" \
    EMAIL_HOST="" \
    EMAIL_HOST_USER="" \
    EMAIL_HOST_PASSWORD="" \
    DEFAULT_FROM_EMAIL="" \
    TWILIO_ACCOUNT_SID="" \
    TWILIO_AUTH_TOKEN="" \
    TWILIO_NUMBER="" \
    BROKER_URL="amqp://guest:guest@rabbitmq//" \
    BACKUP_DIR="/tmp" \
    BACKUP_AWS_ACCESS_KEY_ID="" \
    BACKUP_AWS_SECRET_ACCESS_KEY="" \
    BACKUP_AWS_STORAGE_BUCKET_NAME="" \
    BACKUP_AWS_KEY_PREFIX=""

EXPOSE 80

VOLUME /var/app/static_serve
VOLUME /var/app/upload
VOLUME /var/lib/celery/

ENTRYPOINT ["/docker-entry.sh"]

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
