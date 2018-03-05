FROM node:carbon-alpine AS frontend
WORKDIR /opt/app/
COPY package.json /opt/app/
RUN apk --no-cache add --virtual native-deps \
  g++ make python && \
  npm install --quiet --production && \
  apk del native-deps
COPY . /opt/app/
RUN npm run build:production

FROM python:3.6
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    bzip2
#RUN apk --no-cache add --virtual build-deps \
#    gcc \
#    make \
#    libc-dev \
#    musl-dev \
#    linux-headers \
#    pcre-dev \
#    postgresql-dev \
#    jpeg-dev \
#    zlib-dev
WORKDIR /opt/app/
COPY requirements.txt /opt/app/
RUN python3 -m venv /opt/django-venv && /opt/django-venv/bin/pip install -r /opt/app/requirements.txt
COPY . /opt/app/
# Copy CSS & compiled JavaScript
COPY --from=frontend /opt/app/assets assets
COPY config/wait-for-it.sh /wait-for-it.sh
COPY config/docker-entry.sh /docker-entry.sh
RUN mkdir -p /var/lib/celery && \
    useradd celery && \
    chown celery:celery /var/lib/celery/
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
CMD ["/opt/django-venv/bin/gunicorn", "learnwithpeople.wsgi:application", "--bind", "0.0.0.0:80", "--workers=3"]
