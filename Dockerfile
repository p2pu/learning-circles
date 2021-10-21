FROM node:lts-slim AS frontend
WORKDIR /opt/app/
COPY package.json /opt/app/
COPY p2pu-theme/ /opt/app/p2pu-theme/
RUN npm install --quiet --production
COPY . /opt/app/
RUN npm run build

FROM python:3.6-slim
WORKDIR /opt/app/
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        bzip2 \
        gettext \
        libcairo2 \
        libjpeg-dev \
        libpq-dev \
        libxml2 \
        libxslt-dev \
        openssl \
        postgresql-client \
        wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /opt/app/
RUN python3 -m venv /opt/django-venv \
    && /opt/django-venv/bin/pip install --no-cache-dir -r /opt/app/requirements.txt
COPY . /opt/app/
# Copy CSS & compiled JavaScript
COPY --from=frontend /opt/app/assets assets
COPY config/docker-entry.sh /docker-entry.sh
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN mkdir -p /var/lib/celery && \
    addgroup --gid 1000 celery && \
    useradd --no-log-init --uid 1000 --gid 1000 celery && \
    chown celery:celery /var/lib/celery/
RUN /opt/django-venv/bin/python /opt/app/manage.py compilemessages -l de -l fi -l pl -l pt -l ro
ENV DATABASE_URL="sqlite:////var/app/db.sqlite3" \
    ADMIN_EMAIL="" \
    SECRET_KEY="" \
    EMAIL_HOST="" \
    EMAIL_HOST_USER="" \
    EMAIL_HOST_PASSWORD="" \
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
CMD ["/opt/django-venv/bin/gunicorn", "learnwithpeople.wsgi:application", "--bind", "0.0.0.0:80", "--workers=3"]
