# Deploying Learning Circles to your own server

**Warning**: this guide documents the current setup we use that is not user friendly (at least not yet). While trying to be complete, it is likely that some information required to setup a live hosting environment may be missing.

## Requirements

- Server running Ubuntu 14.04 with at least 1GB or RAM capable of running Docker - we recommend using a Digital Ocean 1GB droplet at 10 USD p/m
- Domain / Subdomain to use
- Twilio account for sending text messages
- Mandril, Sendgrid or Mailgun account for sending email
- AWS account for backups to S3

## Setup

1. Install docker, see (TODO - insert link to howto)
1. Setup postgres - `docker run --name postgres -e POSTGRES_PASSWORD={{DATABASE_ADMIN_PASSWORD}} -v /var/p2pu/lc/postgres:/var/lib/postgresql/data -d postgres:9.3`
 1. Create database & user - `docker exec -i -t postgres psql -U postgres` enter the password you used above and create a user !!TODO insert instructions!!
1. Setup rabbitmq image - `docker run --name rabbitmq -e RABBITMQ_NODENAME=rabbitmq -v /var/p2pu/lc/rabbitmq:/var/lib/rabbitmq rabbitmq:3`
1. Setup Learning Circles app image `

    docker run --name lcapp \
        -e DATABASE_URL="postgres://knight:{{DB_PASSWORD}}@postgres:5432/lcapp" \
        -e ADMIN_EMAIL="{{ADMIN_EMAIL}}" \
        -e SECRET_KEY="{{SECRET_KEY}}" \
        -e EMAIL_HOST="{{EMAIL_HOST}}" \
        -e EMAIL_HOST_USER="{{EMAIL_HOST_USER}}" \
        -e EMAIL_HOST_PASSWORD="{{EMAIL_HOST_PASSWORD}}" \
        -e DEFAULT_FROM_EMAIL="{{DEFAULT_FROM_EMAIL}}" \
        -e AWS_ACCESS_KEY_ID="{{AWS_ACCESS_KEY_ID}}" \
        -e AWS_SECRET_ACCESS_KEY="{{AWS_SECRET_ACCESS_KEY}}" \
        -e AWS_STORAGE_BUCKET_NAME="{{AWS_STORAGE_BUCKET_NAME}}" \
        -e TWILIO_ACCOUNT_SID="{{TWILIO_ACCOUNT_SID}}" \
        -e TWILIO_AUTH_TOKEN="{{TWILIO_AUTH_TOKEN}}" \
        -e TWILIO_NUMBER="{{TWILIO_NUMBER}}" \
        -e BROKER_URL="amqp://guest:guest@rabbitmq//" \
        -e BACKUP_DIR="{{BACKUP_DIR}}" \
        -e BACKUP_AWS_ACCESS_KEY_ID="{{BACKUP_AWS_ACCESS_KEY_ID}}" \
        -e BACKUP_AWS_SECRET_ACCESS_KEY="{{BACKUP_AWS_SECRET_ACCESS_KEY}}" \
        -e BACKUP_AWS_STORAGE_BUCKET_NAME="{{BACKUP_AWS_STORAGE_BUCKET_NAME}}" \
        -e BACKUP_AWS_KEY_PREFIX="{{BACKUP_AWS_KEY_PREFIX}}" \
        -l postgres:postgres
        -l rabbitmq:rabbitmq
        -v /var/p2pu/lc/media:/var/app/upload
        p2pu/learning-circles:latest

1. Point domain name at server IP address


## Customizing the front page

To update copy on the landing page, edit `templates/studygroups/index.html`
To update the footer, edit `templates/footer.html`
To add CSS rules edit `static/sass/p2pu-custom.scss` and then run `sass --scss -I static/sass/ static/sass/p2pu-custom.scss p2pu-custom.css` to compile the CSS.
