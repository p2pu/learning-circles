from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import get_language

from mock import patch
from freezegun import freeze_time

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import Rsvp
from studygroups.models import accept_application
from studygroups.models import create_rsvp
from studygroups.models import generate_all_meetings
from studygroups.rsvp import gen_rsvp_querystring
from studygroups.rsvp import check_rsvp_signature
from studygroups.utils import check_unsubscribe_signature

from studygroups.models import KNOWN_COURSE_PLATFORMS

import calendar
import datetime
import pytz
import re
import urllib.request, urllib.parse, urllib.error
import json

class MockChart():
    def generate():
        return "image"

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
        user.is_staff = True
        user.save()


    def test_accept_application(self):
        # TODO remove this test
        self.assertEqual(Application.objects.active().count(), 0)
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.get(pk=1)
        application = Application(**data)
        application.save()
        accept_application(application)
        self.assertEqual(Application.objects.active().count(), 1)


    def test_get_all_meeting_datetimes(self):
        # TODO
        return
        # setup test accross daylight savings time
        sg = StudyGroup.objects.get(pk=1)
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
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = 'US/Central'
        sg.start_date = now.date() + datetime.timedelta(days=3)
        sg.meeting_time = datetime.time(16,0)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        self.assertEqual(Meeting.objects.all().count(),0)
        generate_all_meetings(sg)
        self.assertEqual(Meeting.objects.all().count(),6)
        self.assertEqual(sg.next_meeting().meeting_datetime().tzinfo.zone, 'US/Central')
        for meeting in Meeting.objects.all():
            self.assertEqual(meeting.meeting_datetime().time(), datetime.time(16,0))


    def test_unapply_signing(self):
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.all().first()
        application = Application(**data)
        application.save()
        qs = application.unapply_link()
        qs = qs[qs.index('?')+1:]
        sig = urllib.parse.parse_qs(qs).get('sig')[0]
        self.assertTrue(check_unsubscribe_signature(application.pk, sig))
        self.assertFalse(check_unsubscribe_signature(application.pk+1, sig))


    def test_rsvp_signing(self):
        meeting_date = timezone.datetime(2015,9,17,17,0, tzinfo=timezone.utc)
        qs = gen_rsvp_querystring('test@mail.com', '1', meeting_date, 'yes')
        sig = urllib.parse.parse_qs(qs).get('sig')[0]
        self.assertTrue(check_rsvp_signature('test@mail.com', '1', meeting_date, 'yes', sig))
        self.assertFalse(check_rsvp_signature('tes@mail.com', '1', meeting_date, 'yes', sig))
        self.assertFalse(check_rsvp_signature('test@mail.com', '2', meeting_date, 'yes', sig))
        self.assertFalse(check_rsvp_signature('test@mail.com', '1', meeting_date, 'no', sig))
        meeting_date = timezone.datetime(2015,9,18,17,0, tzinfo=timezone.utc)
        self.assertFalse(check_rsvp_signature('test@mail.com', '1', meeting_date, 'yes', sig))


    def test_create_rsvp(self):
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.get(pk=1)
        application = Application(**data)
        application.save()
        sg = StudyGroup.objects.get(pk=1)
        meeting_date = timezone.now()
        sgm = Meeting(
            study_group=sg,
            meeting_time=meeting_date.time(),
            meeting_date=meeting_date.date()
        )
        sgm.save()
        sgm = Meeting(
            study_group=sg,
            meeting_time=meeting_date.time(),
            meeting_date=meeting_date.date() + datetime.timedelta(weeks=1)
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


    def test_new_study_group_email(self):
        facilitator = User.objects.create_user('facil', 'facil@test.com', 'password')
        sg = StudyGroup(
            course=Course.objects.first(),
            facilitator=facilitator,
            description='blah',
            venue_name='ACME publich library',
            venue_address='ACME rd 1',
            venue_details='venue_details',
            city='city',
            latitude=0,
            longitude=0,
            start_date=datetime.date(2010,1,1),
            end_date=datetime.date(2010,1,1) + datetime.timedelta(weeks=6),
            meeting_time=datetime.time(12,0),
            duration=90,
            timezone='SAST',
            facilitator_goal='the_facilitator_goal',
            facilitator_concerns='the_facilitators_concerns'
        )
        sg.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('the_facilitator_goal', mail.outbox[0].body)
        self.assertIn('the_facilitators_concerns', mail.outbox[0].body)
[""]

class TestCourseModel(TestCase):
    fixtures = ['test_courses.json', 'test_studygroups.json', 'test_applications.json', 'test_survey_responses.json']

    def test_calculate_ratings(self):
        course = Course.objects.get(pk=3)

        self.assertEqual(course.overall_rating, None)
        self.assertEqual(course.rating_step_counts, "{}")
        self.assertEqual(course.total_ratings, None)

        course.calculate_ratings()

        expected_rating_step_counts = '{"5": 2, "4": 1, "3": 0, "2": 0, "1": 0}'

        self.assertEqual(course.overall_rating, 4.67)
        self.assertEqual(course.rating_step_counts, expected_rating_step_counts)
        self.assertEqual(course.total_ratings, 3)

    def test_calculate_tagdorsements(self):
        course = Course.objects.get(pk=3)

        self.assertEqual(course.tagdorsement_counts, "{}")
        self.assertEqual(course.tagdorsements, "")
        self.assertEqual(course.total_reviewers, None)

        course.calculate_tagdorsements()

        self.assertEqual(course.tagdorsement_counts, '{"Easy to use": 1, "Good for first time facilitators": 0, "Great for beginners": 1, "Engaging material": 1, "Learners were very satisfied": 1, "Led to great discussions": 1}')
        self.assertEqual(course.tagdorsements, 'Easy to use, Great for beginners, Engaging material, Learners were very satisfied, Led to great discussions')
        self.assertEqual(course.total_reviewers, 1)


    def test_detect_platform_from_link(self):
        course = Course.objects.get(pk=4)

        self.assertEqual(course.platform, "")

        course.detect_platform_from_link()

        self.assertEqual(course.platform, KNOWN_COURSE_PLATFORMS["www.khanacademy.org/"])





