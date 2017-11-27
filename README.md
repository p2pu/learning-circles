# Learning circles [![Build Status](https://travis-ci.org/p2pu/learning-circles.svg?branch=master)](https://travis-ci.org/p2pu/learning-circles)

Learning circles are study groups that meet weekly at a physical location to work together through an online course.

This is the source code for the online dashboard that helps facilitators organize and run their learning circles. You can find the dashboard at [learningcircles.p2pu.org](https://learningcircles.p2pu.org/) or see the [online user documentation](http://learning-circles.readthedocs.org/en/latest/) for a guide on how to use the dashboard and a description on the functionality provided.

# What are the future plans

We maintain a [feature roadmap](https://github.com/p2pu/learning-circles/wiki/Roadmap) where you can see what we are currently working on and what we are planning to do.

# Get involved with development

## Setup for development

The following commands will setup a local Django environment that you can use for development. It assumes that you have python 2.7 available and set as the default python version.

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py syncdb
python manage.py runserver
```

## Compile JavaScript files

```
npm install
./node_modules/.bin/webpack --config webpack.config.js --watch
```

## Generate strings for translation

    python manage.py makemessages -l es -l fr -i venv
    python manage.py makemessages -l es -l fr -i venv -i node_modules -i assets/dist/* -i docs -d djangojs -e jsx,js

Translation is done using [Transifex](https://www.transifex.com/p2pu/learning-circles/)
