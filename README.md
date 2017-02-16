Learning circles are study groups that meet weekly to work through an online course.

This application is intended to help learners and facilitators to run learning circles. It also offers an overview of all learning circles.

[![Build Status](https://travis-ci.org/p2pu/learning-circles.svg?branch=master)](https://travis-ci.org/p2pu/learning-circles)

Learners can

- learn more about what a learning circle is
- see a list of learning circles 
- sign up for a learning circle using either email of or a mobile number
- RSVP for weekly learning circle meetings

Facilitators can

- See who signed up for a learning circle.
- Send messages to learners
- Customize automatic weekly reminders
- Update details for a learning circle meeting
- See who is coming to a learning circle meeting
- Capture feedback for a learning circle meeting

Organizers can

- see feedback from facilitators
- see what meetings are happening each week
- receive weekly updates on what happened in learning circles the previous week
- manage courses
- manage study groups
- manage facilitators


## Documentation

For complete documentation on installing and using this software, see our [online documentation here](http://learning-circles.readthedocs.org/en/latest/).

## Setup for development

The following commands will setup a local django environment that you can use for development. It assumes that you have python 2.7 available and set as the default python version.

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
