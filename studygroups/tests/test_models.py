from django.test import TestCase
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User
from django.utils import timezone

from mock import patch

from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import accept_application
from studygroups.models import next_meeting_date
from studygroups.models import generate_reminder

import calendar
import datetime
import pytz

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
        next_date = next_meeting_date(sg)
        self.assertEquals(calendar.day_name[next_date.weekday()], sg.day)
        self.assertTrue(next_date > now)
        diff = next_date - now
        self.assertTrue(diff < datetime.timedelta(weeks=1))
        self.assertTrue(diff > datetime.timedelta())
        self.assertEquals(sg.time, next_date.time())


    def test_generate_reminder(self):
        # Make sure we don't generate a reminder more than 3 days before
        sg = StudyGroup.objects.all()[0]
        meeting = timezone.now() + datetime.timedelta(days=3, minutes=10)
        sg.day = calendar.day_name[meeting.astimezone(pytz.timezone(sg.timezone)).weekday()]
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 0)

        # Make sure we generate a reminder less than three days before
        sg = StudyGroup.objects.all()[0]
        meeting = timezone.now() + datetime.timedelta(days=2, minutes=50)
        sg.day = calendar.day_name[meeting.astimezone(pytz.timezone(sg.timezone)).weekday()]
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        print(reminder.meeting_time)
        self.assertEqual(reminder.meeting_time, next_meeting_date(sg))

        # Make sure we do it only once
        sg = StudyGroup.objects.all()[0]
        meeting = timezone.now() + datetime.timedelta(days=2)
        sg.day = calendar.day_name[meeting.astimezone(pytz.timezone(sg.timezone)).weekday()]
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
