# Learning circles [![Build Status](https://travis-ci.org/p2pu/learning-circles.svg?branch=master)](https://travis-ci.org/p2pu/learning-circles)

Learning circles are study groups that meet weekly at a physical location to work together through an online course.

This is the source code for the online dashboard that helps facilitators organize and run their learning circles. You can find the dashboard at [learningcircles.p2pu.org](https://learningcircles.p2pu.org/) or see the [online user documentation](https://learning-circles-user-manual.readthedocs.io/en/latest/) for a guide on how to use the dashboard and a description on the functionality provided.

# Development

## Run it locally

Install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).

Run the following commands in the project directory:

```
docker-compose up
```

In a new shell:

```
docker-compose exec postgres psql -U postgres -c "create user lc WITH PASSWORD 'password';"
docker-compose exec postgres psql -U postgres -c "create database lc with owner lc;"
docker-compose exec postgres psql -U postgres -c "ALTER USER lc CREATEDB;"
docker-compose restart learning-circles
docker-compose exec learning-circles /opt/django-venv/bin/python manage.py migrate
```

You should now be able to open the dashboard on http://localhost:8000/. Any changes you make to local Python files will be reflected

To run the tests:

```
docker-compose -f docker-compose.test.yml up
docker-compose exec learning-circles /opt/django-venv/bin/python manage.py test
```

To restore the database from an .sql file:
```
docker container exec -i $(docker-compose ps -q postgres) psql -U postgres lc < <filename>.sql
```

## Deploying the code

We maintain a set of ansible roles to deploy learning circles in a repo called [marvin](https://github.com/p2pu/marvin). If you wish to deploy your own version, that will serve as a good guide to set up your own deployment.

## Quick guide to the code

- Django, Postgres, Celery+RabbitMQ for async tasks.
- Front-end functionality is a mix of old-school Django views and React + API backend.
- An API is provided for use by https://www.p2pu.org and team sites.
- Site provides identity for Discourse SSO hosted at https://community.p2pu.org
- Most code resides in the studygroups app.
- Translation is done using [Transifex](https://www.transifex.com/p2pu/learning-circles/). Updated translation files are manually pulled from transifex.
- Database and uploaded files are backed up and uploaded to AWS S3
- Messaging is handled by mailgun, although we use SMTP for sending, so any service can be used for that. The announce list uses mailgun webhook functionality.
- We use Typeform surveys, the surveys are embedded on the site and periodically synced to the db.
