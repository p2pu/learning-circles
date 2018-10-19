# Learning circles [![Build Status](https://travis-ci.org/p2pu/learning-circles.svg?branch=master)](https://travis-ci.org/p2pu/learning-circles)

Learning circles are study groups that meet weekly at a physical location to work together through an online course.

This is the source code for the online dashboard that helps facilitators organize and run their learning circles. You can find the dashboard at [learningcircles.p2pu.org](https://learningcircles.p2pu.org/) or see the [online user documentation](http://learning-circles.readthedocs.org/en/latest/) for a guide on how to use the dashboard and a description on the functionality provided.

# What are the future plans

We maintain a [feature roadmap](https://github.com/p2pu/learning-circles/wiki/Roadmap) where you can see what we are currently working on and what we are planning to do.

# Development

## Development environment

You will need python 3.6 with virtualenv and node v8 available for development.

This section assumes that you have python 3.6 available and set as the default python version and Node.js v8. If that is not the case, please see https://python.org and https://nodejs.org respectively for instruction on how to set it up. If you are running other versions of node on your computer, it is recommended that you use a tool like nvm to manage the different versions.


The shortest path to a running environment is:

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py syncdb
python manage.py collectstatic
python manage.py runserver
```

To compile JavaScript resources, run

```
npm install
npm run build
```

To generate strings for translation

    python manage.py makemessages -l es -l fr -i venv
    python manage.py makemessages -l es -l fr -i venv -i node_modules -i assets/dist/* -i docs -d djangojs -e jsx,js

Translation is done using [Transifex](https://www.transifex.com/p2pu/learning-circles/)


## Using Docker compose

See http://docker.com/ for instructions on installing Docker.

Once you have docker and docker-compose set up, run the following commands in the project directory:

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
docker-compose exec learning-circles /opt/django-venv/bin/python manage.py test
```

To restore the database from an .sql file:
```
docker container exec -i $(docker-compose ps -q postgres) psql -U postgres lc < <filename>.sql
```
