# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language

from mock import patch

from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import Organizer
from studygroups.models import Rsvp
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import Feedback
from studygroups.models import generate_all_meetings
from studygroups.rsvp import gen_rsvp_querystring

from freezegun import freeze_time

import datetime
import urllib.request, urllib.parse, urllib.error
import json

"""
Tests for when a learner interacts with the system. IOW:
    - signups
    - rsvps
"""
class TestLearnerViews(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    APPLICATION_DATA = {
        'study_group': '1',
        'name': 'Test User',
        'email': 'test@mail.com',
        'mobile': '',
        'goals': 'Personal interest',
        'support': 'thinking how to?',
        'computer_access': 'Both', 
        'use_internet': '2'
    }

    def setUp(self):
        user = User.objects.create_user('admin', 'admin@test.com', 'password')
        user.is_superuser = True
        user.is_staff = True
        user.save()


    def test_submit_application(self):
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        # Make sure notification was sent 
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.APPLICATION_DATA['email'])


    def test_application_welcome_message(self):
        c = Client()
        study_group = StudyGroup.objects.get(pk=1)
        study_group.timezone = 'America/Chicago'
        with freeze_time("2015-03-06 18:55:34"):
            generate_all_meetings(study_group)
            resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        # Make sure notification was sent 
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.APPLICATION_DATA['email'])
        self.assertEqual(mail.outbox[0].cc[0], study_group.facilitator.email)
        self.assertIn('The first meeting will be on Monday, 23 March at 6:30PM', mail.outbox[0].body)


    def test_submit_application_sg_with_custom_q(self):
        study_group = StudyGroup.objects.get(pk=1)
        study_group.signup_question = 'how do you do?'
        study_group.save()
        c = Client()
        data = self.APPLICATION_DATA.copy()
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Application.objects.active().count(), 0)
        self.assertEqual(len(mail.outbox), 0)
        
        data['custom_question'] = 'an actual answer'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        # Make sure notification was sent 
        self.assertEqual(len(mail.outbox), 1)
        signup_questions = json.loads(Application.objects.last().signup_questions)
        self.assertEqual(signup_questions['custom_question'], 'an actual answer')


    def test_submit_application_with_other_goal(self):
        c = Client()
        data = self.APPLICATION_DATA.copy()
        data['goals'] = 'Other'
        data['goals_other'] = 'some goal'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        # Make sure notification was sent 
        self.assertEqual(len(mail.outbox), 1)
        signup_questions = json.loads(Application.objects.last().signup_questions)
        self.assertEqual(signup_questions['goals'], 'Other: some goal')


    def test_update_application(self):
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        # Make sure notification was sent 
        self.assertEqual(len(mail.outbox), 1)

        mail.outbox = []
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')

        self.assertEqual(Application.objects.active().count(), 1)
        self.assertEqual(len(mail.outbox), 0)
        
        data = self.APPLICATION_DATA.copy()
        data['email'] = 'test2@mail.com'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 2)

        data = self.APPLICATION_DATA.copy()
        data['mobile'] = '+12812347890'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 2)

        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 2)

        data = self.APPLICATION_DATA.copy()
        data['mobile'] = '+12812347890'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 2)
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 2)


    def test_unapply(self):
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        app = Application.objects.active().first()
        url = app.unapply_link().replace('https://example.net/', '/')
        resp = c.post(url)
        self.assertRedirects(resp, '/en/')
        self.assertEqual(Application.objects.active().count(), 0)


    def test_receive_sms(self):
        # Test receiving a message
        signup_data = self.APPLICATION_DATA.copy()

        signup_data['mobile'] = '+12812347890'
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)

        mail.outbox = []
        url = '/en/receive_sms/'
        sms_data = {
            'Body': 'The first study group for GED® Prep Math will meet next Thursday, May 7th, from 6:00 pm-7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!',
            'From': '+12812347890'
        }

        sg = StudyGroup.objects.get(pk=1)
        sg.meeting_set.delete()
        sg.start_date = datetime.date(2017,10,1)
        sg.end_date = datetime.date(2017,10,1) + datetime.timedelta(weeks=6)
        generate_all_meetings(sg)

        with freeze_time("2017-10-24 17:55:34"):
            resp = c.post(url, sms_data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.find(signup_data['name']) > 0)
        self.assertTrue(mail.outbox[0].subject.find(signup_data['mobile']) > 0)
        self.assertIn(StudyGroup.objects.get(pk=1).facilitator.email, mail.outbox[0].to)
        self.assertIn('admin@localhost', mail.outbox[0].bcc)

        mail.outbox = []
        with freeze_time("2018-10-24 17:55:34"):
            resp = c.post(url, sms_data)

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.find(signup_data['mobile']) > 0)
        self.assertNotIn(StudyGroup.objects.get(pk=1).facilitator.email, mail.outbox[0].to)
        self.assertIn('admin@localhost', mail.outbox[0].to)


    def test_receive_sms_rsvp(self):
        signup_data = self.APPLICATION_DATA.copy()
        signup_data['mobile'] = '+12812347890'
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        mail.outbox = []

        next_meeting = Meeting()
        next_meeting.study_group = StudyGroup.objects.get(pk=signup_data['study_group'])
        next_meeting.meeting_time = (timezone.now() + datetime.timedelta(days=1)).time()
        next_meeting.meeting_date = timezone.now().date() + datetime.timedelta(days=1)
        next_meeting.save()

        url = '/en/receive_sms/'
        sms_data = {
            'Body': 'Sorry, I won\'t make it, have family responsibilities this week :(',
            'From': '+12812347890'
        }
        resp = c.post(url, sms_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.find('+12812347890') > 0)
        self.assertTrue(mail.outbox[0].subject.find('Test User') > 0)
        self.assertIn(StudyGroup.objects.get(pk=1).facilitator.email, mail.outbox[0].to)
        self.assertIn('https://example.net/{0}/rsvp/?user=%2B12812347890&study_group=1&meeting_date={1}&attending=yes&sig='.format(get_language(), urllib.parse.quote(next_meeting.meeting_datetime().isoformat())), mail.outbox[0].body)
        self.assertIn('https://example.net/{0}/rsvp/?user=%2B12812347890&study_group=1&meeting_date={1}&attending=no&sig='.format(get_language(), urllib.parse.quote(next_meeting.meeting_datetime().isoformat())), mail.outbox[0].body)


    def test_receive_random_sms(self):
        c = Client()
        url = '/en/receive_sms/'
        sms_data = {
            'Body': 'Sorry, I won\'t make it, have family responsibilities this week :(',
            'From': '+12812344321'
        }
        resp = c.post(url, sms_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.find('+12812344321') > 0)
        self.assertFalse(mail.outbox[0].subject.find('Test User') > 0)
        self.assertIn('admin@localhost', mail.outbox[0].to)


    def test_receive_sms_optout(self):
        # Test receiving a message
        signup_data = self.APPLICATION_DATA.copy()

        signup_data['mobile'] = '+12812347890'
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)

        mail.outbox = []
        url = '/en/receive_sms/'
        sms_data = {
            'Body': 'STOP',
            'From': '+12812347890'
        }

        resp = c.post(url, sms_data)
        self.assertEqual(len(mail.outbox), 0)
        sg = StudyGroup.objects.get(pk=signup_data['study_group'])
        self.assertNotEqual(sg.application_set.all().first().mobile_opt_out_at, None)


    def test_rsvp_view(self):
        # Setup data for RSVP -> StudyGroup + Signup + Meeting in future

        c = Client()
        study_group = StudyGroup.objects.get(pk=1)
        meeting_time = timezone.now() + datetime.timedelta(days=2)
        study_group_meeting = Meeting(
            study_group=study_group,
            meeting_time=meeting_time.time(),
            meeting_date=meeting_time.date()
        )
        study_group_meeting.save()

        signup_data = self.APPLICATION_DATA.copy()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)

        qs = gen_rsvp_querystring(
            signup_data['email'],
            study_group.pk,
            study_group_meeting.meeting_datetime(),
            'yes'
        )
        url = '/en/rsvp/?{0}'.format(qs)

        # Generate RSVP link
        # visit link
        self.assertEqual(0, Rsvp.objects.count())
        resp = c.get(url)
        self.assertEqual(1, Rsvp.objects.count())
        self.assertTrue(Rsvp.objects.first().attending)

        qs = gen_rsvp_querystring(
            signup_data['email'],
            study_group.pk,
            study_group_meeting.meeting_datetime(),
            'no'
        )
        url = '/en/rsvp/?{0}'.format(qs)
        self.assertEqual(1, Rsvp.objects.count())
        resp = c.get(url)
        self.assertEqual(1, Rsvp.objects.count())
        self.assertFalse(Rsvp.objects.first().attending)

        # Test RSVP with mobile number
        signup_data = self.APPLICATION_DATA.copy()
        signup_data['email'] = 'mmmmmm@lllll.ces'
        signup_data['mobile'] = '+12812347890'
        
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 2)

        qs = gen_rsvp_querystring(
            signup_data['mobile'],
            study_group.pk,
            study_group_meeting.meeting_datetime(),
            'yes'
        )
        url = '/en/rsvp/?{0}'.format(qs)

        # Generate RSVP link
        # visit link
        c = Client()
        Rsvp.objects.all().delete()
        self.assertEqual(0, Rsvp.objects.count())
        resp = c.get(url)
        self.assertEqual(1, Rsvp.objects.count())
        self.assertTrue(Rsvp.objects.first().attending)


    @patch('studygroups.forms.send_message')
    def test_optout_view(self, send_message):
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        app = Application.objects.active().first()

        # test for email
        mail.outbox = []
        resp = c.post('/en/optout/', {'email': app.email} )
        self.assertRedirects(resp, '/en/')
        self.assertEqual(Application.objects.active().count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(app.unapply_link(), mail.outbox[0].body)

        # test for mobile
        data = self.APPLICATION_DATA.copy()
        data['email'] = 'some@other.mail'
        data['mobile'] = '+12812347777'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 2)
        app = Application.objects.active().last()
        self.assertEqual(app.mobile, data['mobile'])

        mail.outbox = []
        resp = c.post('/en/optout/', {'mobile': app.mobile} )
        self.assertRedirects(resp, '/en/')
        self.assertEqual(Application.objects.active().count(), 1)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(send_message.called)


    def test_study_group_learner_feedback(self):
        c = Client()
        sg = StudyGroup.objects.get(pk=1)
        learner = Application.objects.create(
            study_group=sg,
            email='learner@mail.com',
            signup_questions='{"goals": "nothing"}',
            accepted_at=timezone.now()
        )
        url = '/en/studygroup/{}/feedback/?learner={}&goal=2'.format(sg.uuid, learner.uuid)
        resp = c.get(url)
        redirect_url = '/en/studygroup/{}/feedback/'.format(sg.uuid)
        self.assertRedirects(resp, redirect_url)
        learner.refresh_from_db()
        self.assertEqual(learner.goal_met, 2)


    def test_study_group_learner_feedback_uuid_error(self):
        c = Client()
        sg = StudyGroup.objects.get(pk=1)
        learner = Application.objects.create(
            study_group=sg,
            email='learner@mail.com',
            signup_questions='{"goals": "nothing"}',
            accepted_at=timezone.now()
        )
        url = '/en/studygroup/{}/feedback/?learner={}&goal=2'.format(sg.uuid, '00ce18b9-b65d-4e10-8a6e-1b30d3ddc77e')
        resp = c.get(url)
        redirect_url = '/en/studygroup/{}/feedback/'.format(sg.uuid)
        self.assertRedirects(resp, redirect_url)
        learner.refresh_from_db()
        self.assertEqual(learner.goal_met, None)


    def test_study_group_learner_feedback_no_goal(self):
        c = Client()
        sg = StudyGroup.objects.get(pk=1)
        learner = Application.objects.create(
            study_group=sg,
            email='learner@mail.com',
            signup_questions='{}',
            accepted_at=timezone.now()
        )
        url = '/en/studygroup/{}/feedback/?learner={}'.format(sg.uuid, learner.uuid)
        resp = c.get(url)
        redirect_url = '/en/studygroup/{}/feedback/'.format(sg.uuid)
        self.assertRedirects(resp, redirect_url)
        learner.refresh_from_db()
        self.assertEqual(learner.goal_met, None)
