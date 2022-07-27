from icalendar import Calendar, Event
from icalendar import vCalAddress, vText


def make_meeting_ics(meeting):
    study_group = meeting.study_group
    cal = Calendar()
    cal.add('prodid', '-//learningcircles.p2pu.org//LearningCircles')
    cal.add('version', '2.0')
    event = Event()
    event.add('summary', str(meeting))
    event.add('dtstart', meeting.meeting_datetime())
    event.add('dtend', meeting.meeting_datetime_end())

    # Only use the first facilitator or default to created_by
    facilitator = study_group.facilitator
    if study_group.cofacilitators.count():
        facilitator = study_group.cofacilitators.first().user
    organizer = vCalAddress('MAILTO:{}'.format(facilitator.email))
    organizer.params['cn'] = vText(facilitator.first_name)
    organizer.params['role'] = vText('Facilitator')
    event['organizer'] = organizer
    event['location'] = vText('{}, {}, {}, {}'.format(
        study_group.venue_name,
        study_group.city,
        study_group.region,
        study_group.country
    ))

    event['uid'] = '{}-{}@p2pu'.format(study_group.uuid, meeting.pk)
    event.add('priority', 5)

    #attendee = vCalAddress('MAILTO:maxm@example.com')
    #attendee.params['cn'] = vText('Max Rasmussen')
    #attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
    #event.add('attendee', attendee, encode=0)

    cal.add_component(event)
    return cal.to_ical().decode()
