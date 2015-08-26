Organize study groups meeting in a physical location taking online courses.

[![](https://travis-ci.org/p2pu/knight-app.svg)](https://travis-ci.org/p2pu/knight-app)

Users can

- see a list of study groups
- apply for one or more study groups
- RSVP to show that they will come to a study group

Facilitators can

- See who signed up for a learning circle (and manage the signups)
- Send messages to signups
- Add custom messaging to meeting reminders
- Update details for a learning circle meeting
- See who is coming to a learning circle meeting
- Capture feedback for a learning circle meeting

Organizers can

- add courses
- add study groups
- add facilitators

## Installation

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py syncdb
python manage.py runserver
```
