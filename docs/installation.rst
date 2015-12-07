Deploying Learning Circles to your own server
=============================================

This guide runs you through the steps needed to setup the Learning Cicles web app on you own server. To follow these instructions you should be comfortable using the linux command line and following basic instructions. Most of what you need to do is straight forward, but should you run into any trouble, you can ask for help on our [forum](https://community.p2pu.org/)

If you find that you need to do anything different or that some steps or info is missing, please let us know on the forum.

Requirements
------------

* A server running Ubuntu 14.04 with > 1GB of RAM capable of running Docker - we recommend using a Digital Ocean 1GB droplet at 10 USD p/m (If you use [this link](https://www.digitalocean.com/?refcode=d0d9b388d642) you get 10 USD credit and we get 25 USD if you spend 25 USD or more). **The rest of this guide will assume that you are running Ubuntu 14.04 on DigitalOcean**
* Domain / Subdomain to use (You can use [namecheap](https://www.namecheap.com/))
* [Twilio](https://www.twilio.com/) account for sending text messages
* [Mandril](http://mandrill.com/), [Sendgrid](http://sendgrid.com/) or [Mailgun](http://www.mailgun.com/) account for sending email
* [Amazon Web Services](http://aws.amazon.com/) account for backups to S3
  
Setup
-----

Install docker, see instructions [here](https://docs.docker.com/engine/installation/ubuntulinux/)

Download [this file](https://github.com/p2pu/knight-app/raw/master/docs/env.txt) to /var/p2pu/lc/env.txt and edit the environment variables.

Setup postgres: ``docker run --name postgres --env-file=/var/p2pu/lc/env.txt -v /var/p2pu/lc/postgres:/var/lib/postgresql/data -d postgres:9.3``

Create database & user::

    docker exec -i -t postgres psql -U postgres` and type the value of `POSTGRES_PASSWORD
    CREATE USER p2pu password <insertyourpassword>;
    CREATE DATABASE learningcircles;
    GRANT ALL PRIVILEGES ON DATABASE learningcircles to p2pu;

type ``exit`` to quit psql or press CTRL+D

Setup rabbitmq image: ``docker run --name rabbitmq -e RABBITMQ_NODENAME=rabbitmq -v /var/p2pu/lc/rabbitmq:/var/lib/rabbitmq -d rabbitmq:3``

Setup Learning Circles app: ``docker run --name lcapp --env-file=/var/p2pu/lc/env.txt --link postgres:postgres --link rabbitmq:rabbitmq -v /var/p2pu/lc/media:/var/app/upload -p 80:80 -d p2pu/learning-circles:latest``

Create a superuser: ``docker exec -i -t lcapp /var/django-venv/bin/python /var/app/manage.py createsuperuser``

Create a A record to point to the IP address of your server

Go to http://example.net/en/ to view to page.

Go to http://example.net/en/admin/ and log in with the username and password you created above

Customizing the landing page
----------------------------

**TODO** Fork repository and build own docker image!

To update copy on the landing page, edit `templates/studygroups/index.html`
To update the footer, edit `templates/footer.html`
To add CSS rules edit `static/sass/p2pu-custom.scss` and then run `sass --scss -I static/sass/ static/sass/p2pu-custom.scss p2pu-custom.css` to compile the CSS.
