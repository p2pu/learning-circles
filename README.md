Organize study groups meeting in a physical location taking online courses.

[![](https://travis-ci.org/p2pu/knight-app.svg)](https://travis-ci.org/p2pu/knight-app)

Users can

- see a list of courses and study groups
- sign up for a study group

Organizers can

- add courses
- add study groups
- send emails to study groups

## Installation

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py syncdb
python manage.py runserver
```
