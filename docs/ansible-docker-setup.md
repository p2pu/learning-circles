# Deploying Learning Circles to your own server

**Warning**: this guide documents the current setup we use that is in no way user friendly! While trying to be complete, it is very likely that it does not contain all the information required to setup a live hosting environment.

## Requirements

- Host server running Ubuntu 14.04 with at least 1GB or RAM capable of running Docker
- Twilio account for sending text messages
- AWS account for backups to S3
- Mandril, Sendgrid or Mailgun account for sending email
- Domain / Subdomain to use
- SSL certificate for hosting website over https

## Setup

1. Check out [marvin](https://github.com/p2pu/marvin/) (our collection of DevOps scripts ), you only need the docker directory
1. Edit docker/site.yml - remove the p2pu-subscribe role
1. Create an inventory file
1. Create a host config file - see roles/knight-app/tasks/main.yml for required config variables
 1. `PG_ADMIN_USER`
 1. `PG_ADMIN_PASSWORD`
 1. `DOMAIN`
 1. ...
1. Copy your SSL certificates to docker/files
1. Run `ansible-playbook site.yml -i inventory.ini`
1. Access your application 
