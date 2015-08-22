from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User
from django.utils import timezone

from mock import patch

from studygroups.models import StudyGroup
from studygroups.models import StudyGroupMeeting
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import Rsvp
from studygroups.models import accept_application
from studygroups.models import next_meeting_date
from studygroups.models import generate_reminder
from studygroups.models import gen_rsvp_querystring
from studygroups.models import check_rsvp_signature
from studygroups.models import create_rsvp

import calendar
import datetime
import pytz
import re

# Create your tests here.
class TestSignupModels(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    APPLICATION_DATA = {
        'name': 'Test User',
        'contact_method': 'Email',
        'email': 'test@mail.com',
        'computer_access': 'Yes', 
        'goals': 'try hard',
        'support': 'thinking how to?',
        'study_group': '1',
    }


    def setUp(self):
        user = User.objects.create_user('admin', 'admin@test.com', 'password')


    @patch('studygroups.views.send_message')
    def test_accept_application(self, send_message):
        # TODO remove this test
        self.assertEqual(Application.objects.all().count(),0)
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.all()[0]
        application = Application(**data)
        application.save()
        accept_application(application)
        self.assertEqual(Application.objects.all().count() ,1)

    
    def test_next_meeting_date(self):
        sg = StudyGroup.objects.all()[0]
        now = timezone.now()
        sg.start_date = now - datetime.timedelta(weeks=2)
        sg.end_date = now + datetime.timedelta(weeks=2)
        next_date = next_meeting_date(sg)
        self.assertEquals(calendar.day_name[next_date.weekday()], sg.day)
        self.assertTrue(next_date > now)
        diff = next_date - now
        self.assertTrue(diff < datetime.timedelta(weeks=1))
        self.assertTrue(diff > datetime.timedelta())
        self.assertEquals(sg.time, next_date.time())


    def test_next_meeting_date_in_range(self):
        sg = StudyGroup.objects.all()[0]
        now = timezone.now()
        sg.start_date = now + datetime.timedelta(weeks=4)
        sg.end_date = now + datetime.timedelta(weeks=10)
        next_date = next_meeting_date(sg)
        self.assertEquals(calendar.day_name[next_date.weekday()], sg.day)
        self.assertTrue(next_date > now)
        diff = next_date - now
        self.assertTrue(next_date >= sg.start_date)
        self.assertTrue(next_date <= sg.end_date)
        self.assertEquals(sg.time, next_date.time())


    def test_generate_reminder(self):
        # Make sure we don't generate a reminder more than 3 days before
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)
        sg = StudyGroup.objects.all()[0]
        sg.start_date = now - datetime.timedelta(weeks=2)
        sg.end_date = now + datetime.timedelta(weeks=2)
        meeting = timezone.now() + datetime.timedelta(days=3, minutes=10)
        sg.day = calendar.day_name[meeting.astimezone(pytz.timezone(sg.timezone)).weekday()]
        sg.time = meeting.astimezone(pytz.timezone(sg.timezone)).time()
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 0)

        # Make sure we generate a reminder less than three days before
        sg = StudyGroup.objects.all()[0]
        sg.start_date = now - datetime.timedelta(weeks=2)
        sg.end_date = now + datetime.timedelta(weeks=2)
        meeting = timezone.now() + datetime.timedelta(days=2, minutes=50)
        sg.day = calendar.day_name[meeting.astimezone(pytz.timezone(sg.timezone)).weekday()]
        sg.time = meeting.astimezone(pytz.timezone(sg.timezone)).time()
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        #print(reminder.meeting_time)
        self.assertEqual(reminder.meeting_time, next_meeting_date(sg))
        #TODO check that email was sent to site admin
        #TODO test with unicode in generated email subject

        # Make sure we do it only once
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)

    def test_no_reminders_for_old_studygroups(self):
        # Make sure we don't generate a reminder more than 3 days before
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)

        # Make sure we don't generate a reminder for old study groups
        sg = StudyGroup.objects.all()[0]
        sg.start_date = now - datetime.timedelta(weeks=10)
        sg.end_date = now - datetime.timedelta(weeks=2)
        meeting = timezone.now() + datetime.timedelta(days=2, minutes=50)
        sg.day = calendar.day_name[meeting.astimezone(pytz.timezone(sg.timezone)).weekday()]
        sg.time = meeting.astimezone(pytz.timezone(sg.timezone)).time()
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 0)


    def test_no_reminders_for_future_studygroups(self):
        # Make sure we don't generate a reminder more than 3 days before
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)

        # Make sure we don't generate a reminder for old study groups
        sg = StudyGroup.objects.all()[0]
        sg.start_date = now + datetime.timedelta(weeks=2)
        sg.end_date = now + datetime.timedelta(weeks=8)
        meeting = timezone.now() + datetime.timedelta(days=2, minutes=50)
        sg.day = calendar.day_name[meeting.astimezone(pytz.timezone(sg.timezone)).weekday()]
        sg.time = meeting.astimezone(pytz.timezone(sg.timezone)).time()
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 0)


    def test_rsvp_signing(self):
        qs = gen_rsvp_querystring('test@mail.com', '1', '2015-09-17 17:00Z', 'yes')
        sig = re.search(r'sig=(?P<sig>[a-f,A-F,0-9]+)*', qs).group(1)
        self.assertTrue(check_rsvp_signature('test@mail.com', '1', '2015-09-17 17:00Z', 'yes', sig))
        self.assertFalse(check_rsvp_signature('tes@mail.com', '1', '2015-09-17 17:00Z', 'yes', sig))
        self.assertFalse(check_rsvp_signature('test@mail.com', '2', '2015-09-17 17:00Z', 'yes', sig))
        self.assertFalse(check_rsvp_signature('test@mail.com', '1', '2015-08-17 17:00Z', 'yes', sig))
        self.assertFalse(check_rsvp_signature('test@mail.com', '1', '2015-09-17 17:00Z', 'no', sig))


    def test_create_rsvp(self):
        self.assertEqual(Rsvp.objects.all().count(), 0)
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.all()[0]
        application = Application(**data)
        application.save()
        sg = StudyGroup.objects.all()[0]
        meeting_date = timezone.now()
        sgm = StudyGroupMeeting(study_group=sg, meeting_time=meeting_date)
        sgm.save()
        #create_rsvp('test@mail.com', sg.id, meeting_date.strftime("%Y%m%dT%H:%M%Z"), 'yes')
        create_rsvp('test@mail.com', sg.id, meeting_date, 'yes')
        self.assertEqual(Rsvp.objects.all().count(), 1)

    
    def test_create_study_group_meeting(self):
        # TODO
        pass
