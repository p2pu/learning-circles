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
from studygroups.models import Facilitator
from studygroups.models import Rsvp
from studygroups.rsvp import gen_rsvp_querystring

import datetime
import urllib

# Create your tests here.
class TestSignupViews(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    APPLICATION_DATA = {
        'study_group': '1',
        'name': 'Test User',
        'email': 'test@mail.com',
        'goals': 'try hard',
        'support': 'thinking how to?',
        'computer_access': 'Both', 
        'send_email': '2', 
        'delete_spam': '2', 
        'search_online': '2', 
        'browse_video': '2', 
        'online_shopping': '2', 
        'mobile_apps': '2', 
        'web_safety': '2'
    }

    def setUp(self):
        user = User.objects.create_user('admin', 'admin@test.com', 'password')
        user.is_superuser = True
        user.is_staff = True
        user.save()

# TODO - test at least every view!

    def test_submit_application(self):
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 1)
        # Make sure notification was sent 
        self.assertEqual(len(mail.outbox), 1)


    def test_update_application(self):
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 1)
        # Make sure notification was sent 
        self.assertEqual(len(mail.outbox), 1)
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 1)
        
        data = self.APPLICATION_DATA.copy()
        data['email'] = 'test2@mail.com'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 2)

        data = self.APPLICATION_DATA.copy()
        del data['email']
        data['mobile'] = '123-456-7890'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 3)
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 3)
        data = self.APPLICATION_DATA.copy()
        data['mobile'] = '123-456-7890'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 3)
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 3)


    def test_unapply(self):
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 1)
        app = Application.objects.first()
        url = app.unapply_link().replace('https://example.net/', '/')
        resp = c.post(url)
        self.assertRedirects(resp, '/en/')
        self.assertEquals(Application.objects.all().count(), 0)

    
    @patch('studygroups.models.send_message')
    def test_send_email(self, send_message):
        # Test sending a message
        c = Client()
        c.login(username='admin', password='password')
        signup_data = self.APPLICATION_DATA.copy()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 1)
        mail.outbox = []

        url = '/en/studygroup/{0}/message/compose/'.format(signup_data['study_group'])
        email_body = u'Hi there!\n\nThe first study group for GED® Prep Math will meet this Thursday, May 7th, from 6:00 pm - 7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!\nFor any questions you can contact Emily at emily@p2pu.org.\n\nSee you soon'
        mail_data = {
            u'study_group': signup_data['study_group'],
            u'email_subject': u'GED® Prep Math study group meeting Thursday 7 May 6:00 PM at Edgewater', 
            u'email_body': email_body, 
            u'sms_body': 'The first study group for GED® Prep Math will meet next Thursday, May 7th, from 6:00 pm-7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!'
        }
        resp = c.post(url, mail_data)
        self.assertRedirects(resp, '/en/facilitator/')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, mail_data['email_subject'])
        self.assertFalse(send_message.called)
        self.assertIn('https://example.net/en/optout/', mail.outbox[0].body)


    @patch('studygroups.models.send_message')
    def test_send_sms(self, send_message):
        c = Client()
        c.login(username='admin', password='password')
        signup_data = self.APPLICATION_DATA.copy()
        signup_data['mobile'] = '123-456-7890'
        del signup_data['email']
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 1)
        mail.outbox = []

        url = '/en/studygroup/{0}/message/compose/'.format(signup_data['study_group'])
        mail_data = {
            'study_group': signup_data['study_group'],
            'email_subject': 'test', 
            'email_body': 'Email body', 
            'sms_body': 'Sms body'
        }
        resp = c.post(url, mail_data)
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(send_message.called)


    def test_receive_sms(self):
        # Test receiving a message
        signup_data = self.APPLICATION_DATA.copy()
        signup_data['mobile'] = '123-456-7890'
        del signup_data['email']
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 1)

        mail.outbox = []
        url = '/en/receive_sms/'
        sms_data = {
            u'Body': 'The first study group for GED® Prep Math will meet next Thursday, May 7th, from 6:00 pm-7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!',
            u'From': '+11234567890'
        }
        resp = c.post(url, sms_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.find(signup_data['name']) > 0)
        self.assertTrue(mail.outbox[0].subject.find(signup_data['mobile']) > 0)
        self.assertIn(StudyGroup.objects.all()[0].facilitator.email, mail.outbox[0].to)
        self.assertIn('admin@localhost', mail.outbox[0].bcc)


    def test_receive_sms_rsvp(self):
        signup_data = self.APPLICATION_DATA.copy()
        signup_data['mobile'] = '123-456-7890'
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 1)
        mail.outbox = []

        next_meeting = StudyGroupMeeting()
        next_meeting.study_group = StudyGroup.objects.get(pk=signup_data['study_group'])
        next_meeting.meeting_time = timezone.now() + datetime.timedelta(days=1)
        next_meeting.save()

        url = '/en/receive_sms/'
        sms_data = {
            u'Body': 'Sorry, I won\'t make it, have family responsibilities this week :(',
            u'From': '+11234567890'
        }
        resp = c.post(url, sms_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.find('123-456-7890') > 0)
        self.assertTrue(mail.outbox[0].subject.find('Test User') > 0)
        self.assertIn(StudyGroup.objects.all()[0].facilitator.email, mail.outbox[0].to)
        self.assertIn('https://example.net/{0}/rsvp/?user=123-456-7890&study_group=1&meeting_date={1}&attending=yes&sig='.format(get_language(), urllib.quote(next_meeting.meeting_time.isoformat())), mail.outbox[0].body)
        self.assertIn('https://example.net/{0}/rsvp/?user=123-456-7890&study_group=1&meeting_date={1}&attending=no&sig='.format(get_language(), urllib.quote(next_meeting.meeting_time.isoformat())), mail.outbox[0].body)


    def test_receive_random_sms(self):
        c = Client()
        url = '/en/receive_sms/'
        sms_data = {
            u'Body': 'Sorry, I won\'t make it, have family responsibilities this week :(',
            u'From': '+10987654321'
        }
        resp = c.post(url, sms_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.find('098-765-4321') > 0)
        self.assertFalse(mail.outbox[0].subject.find('Test User') > 0)
        self.assertIn('admin@localhost', mail.outbox[0].to)


    def test_user_forbidden(self):
        user = User.objects.create_user('bob', 'bob@example.net', 'password')
        c = Client()
        c.login(username='bob', password='password')
        def assertForbidden(url):
            resp = c.get(url)
            self.assertEqual(resp.status_code, 403)
        assertForbidden('/en/organize/')
        assertForbidden('/en/report/')
        assertForbidden('/en/report/weekly/')
        assertForbidden('/en/studygroup/1/')
        assertForbidden('/en/studygroup/1/edit/')
        assertForbidden('/en/studygroup/1/message/compose/')
        assertForbidden('/en/studygroup/1/message/edit/1/')
        assertForbidden('/en/studygroup/1/member/add/')
        assertForbidden('/en/studygroup/1/member/1/delete/')
        assertForbidden('/en/studygroup/1/meeting/create/')
        assertForbidden('/en/studygroup/1/meeting/2/edit/')
        assertForbidden('/en/studygroup/1/meeting/2/delete/')
        assertForbidden('/en/studygroup/1/meeting/2/feedback/create/')


    def test_facilitator_access(self):
        User.objects.create_user('bob123', 'bob@example.net', 'password')
        user = User.objects.get(username='bob123')
        sg = StudyGroup.objects.get(pk=1)
        sg.facilitator = user
        sg.save()
        c = Client()
        c.login(username='bob123', password='password')
        def assertAllowed(url):
            resp = c.get(url)
            #TODO not sure if it's a good idea to include 404 here!
            self.assertIn(resp.status_code, [200, 301, 302])

        def assertStatus(url, status):
            resp = c.get(url)
            self.assertEquals(resp.status_code, status)
        assertAllowed('/en/studygroup/1/')
        assertAllowed('/en/studygroup/1/edit/')
        assertAllowed('/en/studygroup/1/message/compose/')
        assertStatus('/en/studygroup/1/message/edit/1/', 404)
        assertAllowed('/en/studygroup/1/member/add/')
        assertStatus('/en/studygroup/1/member/2/delete/', 404)
        assertAllowed('/en/studygroup/1/meeting/create/')
        assertStatus('/en/studygroup/1/meeting/2/edit/', 404)
        assertStatus('/en/studygroup/1/meeting/2/delete/', 404)
        assertStatus('/en/studygroup/1/meeting/2/feedback/create/', 404)


    def test_organizer_access(self):
        User.objects.create_user('bob123', 'bob@example.net', 'password')
        user = User.objects.get(username='bob123')
        Organizer.objects.create(user=user)
        c = Client()
        c.login(username='bob123', password='password')

        def assertAllowed(url):
            resp = c.get(url)
            self.assertIn(resp.status_code, [200, 301, 302])

        def assertStatus(url, status):
            resp = c.get(url)
            self.assertEquals(resp.status_code, status)

        assertAllowed('/en/')
        assertAllowed('/en/organize/')
        assertAllowed('/en/report/')
        assertAllowed('/en/report/weekly/')
        assertAllowed('/en/studygroup/1/')
        assertAllowed('/en/studygroup/1/edit/')
        assertAllowed('/en/studygroup/1/message/compose/')
        assertStatus('/en/studygroup/1/message/edit/1/', 404)
        assertAllowed('/en/studygroup/1/member/add/')
        assertStatus('/en/studygroup/1/member/2/delete/', 404)
        assertAllowed('/en/studygroup/1/meeting/create/')
        assertStatus('/en/studygroup/1/meeting/2/edit/', 404)
        assertStatus('/en/studygroup/1/meeting/2/delete/', 404)
        assertStatus('/en/studygroup/1/meeting/2/feedback/create/', 404)


    def test_rsvp_view(self):
        # Setup data for RSVP -> StudyGroup + Signup + Meeting in future

        c = Client()
        study_group = StudyGroup.objects.all()[0]
        meeting_time = timezone.now() + datetime.timedelta(days=2)
        study_group_meeting = StudyGroupMeeting(
            study_group=study_group,
            meeting_time=meeting_time
        )
        study_group_meeting.save()

        signup_data = self.APPLICATION_DATA.copy()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 1)

        qs = gen_rsvp_querystring(
            signup_data['email'],
            study_group.pk,
            study_group_meeting.meeting_time,
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
            study_group_meeting.meeting_time,
            'no'
        )
        url = '/en/rsvp/?{0}'.format(qs)
        self.assertEqual(1, Rsvp.objects.count())
        resp = c.get(url)
        self.assertEqual(1, Rsvp.objects.count())
        self.assertFalse(Rsvp.objects.first().attending)

        # Test RSVP with mobile number
        signup_data = self.APPLICATION_DATA.copy()
        del signup_data['email']
        signup_data['mobile'] = '123-456-7890'
        
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 2)

        qs = gen_rsvp_querystring(
            signup_data['mobile'],
            study_group.pk,
            study_group_meeting.meeting_time,
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


    def test_organizer_login_redirect(self):
        User.objects.create_user('bob123', 'bob@example.net', 'password')
        user = User.objects.get(username='bob123')
        Organizer.objects.create(user=user)
        c = Client()
        c.login(username='bob123', password='password')
        resp = c.get('/en/login_redirect/')
        self.assertRedirects(resp, '/en/organize/')


    def test_facilitator_login_redirect(self):
        User.objects.create_user('bob123', 'bob@example.net', 'password')
        user = User.objects.get(username='bob123')
        Facilitator.objects.create(user=user)
        c = Client()
        c.login(username='bob123', password='password')
        resp = c.get('/en/login_redirect/')
        self.assertRedirects(resp, '/en/facilitator/')


    @patch('studygroups.forms.send_message')
    def test_optout_view(self, send_message):
        c = Client()
        resp = c.post('/en/signup/foo-bob-1/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 1)
        app = Application.objects.first()

        # test for email
        mail.outbox = []
        resp = c.post('/en/optout/', {'email': app.email} )
        self.assertRedirects(resp, '/en/')
        self.assertEquals(Application.objects.all().count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(app.unapply_link(), mail.outbox[0].body)

        # test for mobile
        data = self.APPLICATION_DATA.copy()
        del data['email']
        data['mobile'] = '123-456-7777'
        resp = c.post('/en/signup/foo-bob-1/', data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEquals(Application.objects.all().count(), 2)
        app = Application.objects.last()
        self.assertEquals(app.mobile, data['mobile'])

        mail.outbox = []
        resp = c.post('/en/optout/', {'mobile': app.mobile} )
        self.assertRedirects(resp, '/en/')
        self.assertEquals(Application.objects.all().count(), 1)
        self.assertEquals(len(mail.outbox), 0)
        self.assertTrue(send_message.called)


