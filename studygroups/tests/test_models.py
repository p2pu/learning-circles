from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import get_language

from mock import patch

from studygroups.models import StudyGroup
from studygroups.models import StudyGroupMeeting
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import Rsvp
from studygroups.models import accept_application
from studygroups.models import generate_reminder
from studygroups.models import send_reminder
from studygroups.models import create_rsvp
from studygroups.models import generate_all_meetings
from studygroups.rsvp import gen_rsvp_querystring
from studygroups.rsvp import check_rsvp_signature
from studygroups.utils import gen_unsubscribe_querystring
from studygroups.utils import check_unsubscribe_signature

import calendar
import datetime
import pytz
import re
import urlparse
import urllib
import json

# Create your tests here.
class TestSignupModels(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    APPLICATION_DATA = {
        'name': 'Test User',
        'email': 'test@mail.com',

        'signup_questions': json.dumps({
            'computer_access': 'Yes',
            'goals': 'try hard',
            'support': 'thinking how to?',
        }),
        'study_group': '1',
    }


    def setUp(self):
        user = User.objects.create_user('admin', 'admin@test.com', 'password')


    def test_accept_application(self):
        # TODO remove this test
        self.assertEqual(Application.objects.active().count(), 0)
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.all()[0]
        application = Application(**data)
        application.save()
        accept_application(application)
        self.assertEqual(Application.objects.active().count(), 1)


    def test_get_all_meeting_datetimes(self):
        # TODO
        return
        # setup test accross daylight savings time
        sg = StudyGroup.objects.all()[0]
        sg.timezone = 'US/Central'
        sg.meeting_time = datetime.time(16, 0)
        tz = pytz.timezone(sg.timezone)

        for i in range(56):
            start_date = datetime.date(2015, 1, 1) + datetime.timedelta(weeks=i)
            end_date = start_date + datetime.timedelta(weeks=5)
            sg.start_date = start_date
            sg.end_date = end_date
            meeting_times = get_all_meeting_times(sg)
            self.assertEqual(len(meeting_times), 6)
            self.assertEqual(meeting_times[0].date(), sg.start_date)
            self.assertEqual(meeting_times[-1].date(), sg.end_date)
            for meeting_time in meeting_times:
                self.assertEqual(datetime.time(16,0), meeting_time.time())


    def test_generate_all_meetings(self):
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)
        sg = StudyGroup.objects.all()[0]
        sg.timezone = 'US/Central'
        sg.start_date = now.date() + datetime.timedelta(days=3)
        sg.meeting_time = datetime.time(16,0)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.all()[0]
        self.assertEqual(StudyGroupMeeting.objects.all().count(),0)
        generate_all_meetings(sg)
        self.assertEqual(StudyGroupMeeting.objects.all().count(),6)
        self.assertEqual(sg.next_meeting().meeting_datetime().tzinfo.zone, 'US/Central')
        for meeting in StudyGroupMeeting.objects.all():
            self.assertEqual(meeting.meeting_datetime().time(), datetime.time(16,0))


    def test_dont_generate_reminder_4days_before(self):
        # Make sure we don't generate a reminder more than 4 days before
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)
        sg = StudyGroup.objects.all()[0]
        sg.timezone = now.strftime("%Z")
        sg.start_date = now + datetime.timedelta(days=4, hours=1)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.all()[0]
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 0)


    def test_generate_reminder_4days_before(self):
        # Make sure we generate a reminder less than 4 days before
        now = timezone.now()
        sg = StudyGroup.objects.all()[0]
        sg.timezone = now.strftime("%Z")
        sg.start_date = now.date() + datetime.timedelta(days=3)
        sg.meeting_time = now.time()
        sg.end_date = now.date() + datetime.timedelta(weeks=5, days=3)
        sg.save()
        sg = StudyGroup.objects.all()[0]
        generate_all_meetings(sg)
        self.assertEqual(sg.studygroupmeeting_set.active().count(), 6)
        self.assertTrue(sg.next_meeting().meeting_datetime() - now < datetime.timedelta(days=4))
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        #TODO check that email was sent to site admin
        #TODO test with unicode in generated email subject

        # Make sure we do it only once
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)

    def test_no_reminders_for_old_studygroups(self):
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)

        # Make sure we don't generate a reminder for old study groups
        sg = StudyGroup.objects.all()[0]
        sg.timezone = now.strftime("%Z")
        sg.start_date = now - datetime.timedelta(days=5, weeks=7)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.all()[0]
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 0)


    def test_no_reminders_for_future_studygroups(self):
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)

        # Make sure we don't generate a reminder for future study groups
        sg = StudyGroup.objects.all()[0]
        sg.timezone = now.strftime("%Z")
        sg.start_date = now + datetime.timedelta(days=2, weeks=1)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.all()[0]
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 0)


    @patch('studygroups.models.send_message')
    def test_send_reminder_email(self, send_message):
        now = timezone.now()
        sg = StudyGroup.objects.all()[0]
        sg.timezone = now.strftime("%Z")
        sg.start_date = now - datetime.timedelta(days=5)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.all()[0]
        data = self.APPLICATION_DATA
        data['study_group'] = sg
        application = Application(**data)
        accept_application(application)
        application.save()
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        self.assertEqual(len(mail.outbox), 1)
        send_reminder(reminder)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].to[0], data['email'])
        self.assertFalse(send_message.called)
        self.assertIn('https://example.net/{0}/rsvp/?user=test%40mail.com&study_group=1&meeting_date={1}&attending=yes&sig='.format(get_language(), urllib.quote(sg.next_meeting().meeting_datetime().isoformat())), mail.outbox[1].body)
        self.assertIn('https://example.net/{0}/rsvp/?user=test%40mail.com&study_group=1&meeting_date={1}&attending=no&sig='.format(get_language(), urllib.quote(sg.next_meeting().meeting_datetime().isoformat())), mail.outbox[1].body)
        self.assertIn('https://example.net/{0}/optout/confirm/?user='.format(get_language()), mail.outbox[1].body)


    @patch('studygroups.models.send_message')
    def test_send_reminder_sms(self, send_message):
        now = timezone.now()
        sg = StudyGroup.objects.all()[0]
        sg.timezone = now.strftime("%Z")
        sg.start_date = now - datetime.timedelta(days=5)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.all()[0]
        data = self.APPLICATION_DATA
        data['study_group'] = sg
        application = Application(**data)
        application.save()
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        send_reminder(reminder)
        self.assertEqual(len(mail.outbox), 1)
        #self.assertEqual(mail.outbox[0].subject, mail_data['email_subject'])
        self.assertFalse(send_message.called)


    def test_unapply_signing(self):
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.all().first()
        application = Application(**data)
        application.save()
        qs = application.unapply_link()
        qs = qs[qs.index('?')+1:]
        sig = urlparse.parse_qs(qs).get('sig')[0]
        self.assertTrue(check_unsubscribe_signature(application.pk, sig))
        self.assertFalse(check_unsubscribe_signature(application.pk+1, sig))


    def test_rsvp_signing(self):
        meeting_date = timezone.datetime(2015,9,17,17,0, tzinfo=timezone.utc)
        qs = gen_rsvp_querystring('test@mail.com', '1', meeting_date, 'yes')
        sig = urlparse.parse_qs(qs).get('sig')[0]
        self.assertTrue(check_rsvp_signature('test@mail.com', '1', meeting_date, 'yes', sig))
        self.assertFalse(check_rsvp_signature('tes@mail.com', '1', meeting_date, 'yes', sig))
        self.assertFalse(check_rsvp_signature('test@mail.com', '2', meeting_date, 'yes', sig))
        self.assertFalse(check_rsvp_signature('test@mail.com', '1', meeting_date, 'no', sig))
        meeting_date = timezone.datetime(2015,9,18,17,0, tzinfo=timezone.utc)
        self.assertFalse(check_rsvp_signature('test@mail.com', '1', meeting_date, 'yes', sig))


    def test_create_rsvp(self):
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.all()[0]
        application = Application(**data)
        application.save()
        sg = StudyGroup.objects.all()[0]
        meeting_date = timezone.now()
        sgm = StudyGroupMeeting(
            study_group=sg,
            meeting_time=meeting_date.time(),
            meeting_date=meeting_date.date()
        )
        sgm.save()

        # Test creating an RSVP
        self.assertEqual(Rsvp.objects.all().count(), 0)
        create_rsvp('test@mail.com', sg.id, meeting_date, 'yes')
        self.assertEqual(Rsvp.objects.all().count(), 1)
        self.assertTrue(Rsvp.objects.all().first().attending)

        # Test updating an RSVP
        create_rsvp('test@mail.com', sg.id, meeting_date, 'no')
        self.assertEqual(Rsvp.objects.all().count(), 1)
        self.assertFalse(Rsvp.objects.all().first().attending)
