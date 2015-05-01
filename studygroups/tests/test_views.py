# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User

from mock import patch

from studygroups.models import StudyGroup
from studygroups.models import StudyGroupSignup
from studygroups.models import Application

# Create your tests here.
class TestSignupViews(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    APPLICATION_DATA = {
        'name': 'Test User',
        'contact_method': 'Email',
        'email': 'test@mail.com',
        'computer_access': 'Yes', 
        'goals': 'try hard',
        'support': 'thinking how to?',
        'study_groups': '1',
    }

    SIGNUP_DATA = {
        'study_group_id': '1',
        'username': 'Test User',
        'contact_method': 'Email',
        'email': 'test@mail.com',
    }


    def setUp(self):
        user = User.objects.create_user('admin', 'admin@test.com', 'password')

    @override_settings(ADMINS=('Admin', 'admin@test.com'))
    def test_submit_application(self):
        c = Client()
        resp = c.post('/en/apply/', self.APPLICATION_DATA)
        self.assertRedirects(resp, '/en/')
        self.assertEquals(Application.objects.all().count(), 1)
        self.assertEqual(len(mail.outbox), 1)


    
    @patch('studygroups.views.send_message')
    def test_send_email(self, send_message):
        # Test sending a message
        c = Client()
        c.login(username='admin', password='password')
        signup = StudyGroupSignup(**self.SIGNUP_DATA)
        signup.save()
        url = '/en/organize/studygroup/{0}/email/'.format(signup.study_group_id)
        email_body = u'Hi there!\n\nThe first study group for GED® Prep Math will meet this Thursday, May 7th, from 6:00 pm - 7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!\nFor any questions you can contact Emily at emily@p2pu.org.\n\nSee you soon'
        mail_data = {
            u'study_group_id': signup.study_group_id,
            u'subject': u'GED® Prep Math study group meeting Thursday 7 May 6:00 PM at Edgewater', 
            u'body': email_body, 
            u'sms_body': 'The first study group for GED® Prep Math will meet next Thursday, May 7th, from 6:00 pm-7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!'
        }
        resp = c.post(url, mail_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, mail_data['subject'])
        self.assertFalse(send_message.called)


    @patch('studygroups.views.send_message')
    def test_send_sms(self, send_message):
        c = Client()
        c.login(username='admin', password='password')
        signup_data = self.SIGNUP_DATA
        signup_data['contact_method'] = 'Text'
        signup_data['mobile'] = '123-456-7890'
        signup = StudyGroupSignup(**signup_data)
        signup.save()
        url = '/en/organize/studygroup/{0}/email/'.format(signup.study_group_id)
        mail_data = {
            'study_group_id': signup.study_group_id,
            'subject': 'test', 
            'body': 'Email body', 
            'sms_body': 'Sms body'
        }
        resp = c.post(url, mail_data)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(send_message.called)


    @override_settings(ADMINS=('Admin', 'admin@test.com'))
    def test_receive_sms(self):
        # Test sending a message
        c = Client()
        url = '/en/receive_sms/'
        sms_data = {
            u'Body': 'The first study group for GED® Prep Math will meet next Thursday, May 7th, from 6:00 pm-7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!',
            u'From': '123-456-7890'
        }
        resp = c.post(url, sms_data)
        self.assertEqual(len(mail.outbox), 1)
        #self.assertEqual(mail.outbox[0].subject, mail_data['subject'])


