# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language

from mock import patch

from studygroups.models import StudyGroup
from studygroups.models import StudyGroupMeeting
from studygroups.models import Application
from studygroups.models import Organizer
from studygroups.models import Rsvp
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import Feedback
from studygroups.rsvp import gen_rsvp_querystring

import datetime
import urllib

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
        'goals': 'try hard',
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
        self.assertEquals(Application.objects.active().count(), 1)
        # Make sure notification was sent 
        self.assertEqual(len(mail.outbox), 1)


    def test_update_application(self):
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 1)
        # Make sure notification was sent 
        self.assertEqual(len(mail.outbox), 1)
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 1)
        
        data = self.APPLICATION_DATA.copy()
        data['email'] = 'test2@mail.com'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 2)

        data = self.APPLICATION_DATA.copy()
        data['mobile'] = '+12812347890'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 2)

        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 2)

        data = self.APPLICATION_DATA.copy()
        data['mobile'] = '+12812347890'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 2)
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 2)


    def test_unapply(self):
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 1)
        app = Application.objects.active().first()
        url = app.unapply_link().replace('https://example.net/', '/')
        resp = c.post(url)
        self.assertRedirects(resp, '/en/')
        self.assertEquals(Application.objects.active().count(), 0)


    def test_receive_sms(self):
        # Test receiving a message
        signup_data = self.APPLICATION_DATA.copy()
        signup_data['mobile'] = '+12812347890'
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 1)

        mail.outbox = []
        url = '/en/receive_sms/'
        sms_data = {
            u'Body': 'The first study group for GED® Prep Math will meet next Thursday, May 7th, from 6:00 pm-7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!',
            u'From': '+12812347890'
        }
        resp = c.post(url, sms_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.find(signup_data['name']) > 0)
        self.assertTrue(mail.outbox[0].subject.find(signup_data['mobile']) > 0)
        self.assertIn(StudyGroup.objects.get(pk=1).facilitator.email, mail.outbox[0].to)
        self.assertIn('admin@localhost', mail.outbox[0].bcc)


    def test_receive_sms_rsvp(self):
        signup_data = self.APPLICATION_DATA.copy()
        signup_data['mobile'] = '+12812347890'
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 1)
        mail.outbox = []

        next_meeting = StudyGroupMeeting()
        next_meeting.study_group = StudyGroup.objects.get(pk=signup_data['study_group'])
        next_meeting.meeting_time = (timezone.now() + datetime.timedelta(days=1)).time()
        next_meeting.meeting_date = timezone.now().date() + datetime.timedelta(days=1)
        next_meeting.save()

        url = '/en/receive_sms/'
        sms_data = {
            u'Body': 'Sorry, I won\'t make it, have family responsibilities this week :(',
            u'From': '+12812347890'
        }
        resp = c.post(url, sms_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.find('+12812347890') > 0)
        self.assertTrue(mail.outbox[0].subject.find('Test User') > 0)
        self.assertIn(StudyGroup.objects.get(pk=1).facilitator.email, mail.outbox[0].to)
        self.assertIn('https://example.net/{0}/rsvp/?user=%2B12812347890&study_group=1&meeting_date={1}&attending=yes&sig='.format(get_language(), urllib.quote(next_meeting.meeting_datetime().isoformat())), mail.outbox[0].body)
        self.assertIn('https://example.net/{0}/rsvp/?user=%2B12812347890&study_group=1&meeting_date={1}&attending=no&sig='.format(get_language(), urllib.quote(next_meeting.meeting_datetime().isoformat())), mail.outbox[0].body)


    def test_receive_random_sms(self):
        c = Client()
        url = '/en/receive_sms/'
        sms_data = {
            u'Body': 'Sorry, I won\'t make it, have family responsibilities this week :(',
            u'From': '+12812344321'
        }
        resp = c.post(url, sms_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.find('+12812344321') > 0)
        self.assertFalse(mail.outbox[0].subject.find('Test User') > 0)
        self.assertIn('admin@localhost', mail.outbox[0].to)


    def test_rsvp_view(self):
        # Setup data for RSVP -> StudyGroup + Signup + Meeting in future

        c = Client()
        study_group = StudyGroup.objects.get(pk=1)
        meeting_time = timezone.now() + datetime.timedelta(days=2)
        study_group_meeting = StudyGroupMeeting(
            study_group=study_group,
            meeting_time=meeting_time.time(),
            meeting_date=meeting_time.date()
        )
        study_group_meeting.save()

        signup_data = self.APPLICATION_DATA.copy()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 1)

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
        self.assertEquals(Application.objects.active().count(), 2)

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
        self.assertEquals(Application.objects.active().count(), 1)
        app = Application.objects.active().first()

        # test for email
        mail.outbox = []
        resp = c.post('/en/optout/', {'email': app.email} )
        self.assertRedirects(resp, '/en/')
        self.assertEquals(Application.objects.active().count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(app.unapply_link(), mail.outbox[0].body)

        # test for mobile
        data = self.APPLICATION_DATA.copy()
        data['email'] = 'some@other.mail'
        data['mobile'] = '+12812347777'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.active().count(), 2)
        app = Application.objects.active().last()
        self.assertEquals(app.mobile, data['mobile'])

        mail.outbox = []
        resp = c.post('/en/optout/', {'mobile': app.mobile} )
        self.assertRedirects(resp, '/en/')
        self.assertEquals(Application.objects.active().count(), 1)
        self.assertEquals(len(mail.outbox), 0)
        self.assertTrue(send_message.called)

