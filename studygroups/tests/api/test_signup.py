# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language

from unittest.mock import patch

from studygroups.models import StudyGroup
from studygroups.models import Application

import datetime
import json

class TestApiSignupView(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    APPLICATION_DATA = {
        'learning_circle': '1',
        'name': 'Test User',
        'email': 'test@mail.com',
        'mobile': '',
        'goals': 'try hard',
        'support': 'thinking how to?',
        'computer_access': 'Both',
        'use_internet': '2'
    }

    def setUp(self):
        pass

    def test_valid_signup(self):
        c = Client()
        url = '/api/signup/'
        signup_data = {
            'learning_circle': '1',
            'name': 'User name',
            'email': 'user@mail.com',
            'communications_opt_in': 'false',
            'consent': 'true',
            'mobile': '+12812344321',
            'signup_questions': {
                'goals': 'Learn new stuff',
                'support': 'Help my fellow learners'
            }
        }
        resp = c.post(url, data=json.dumps(signup_data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "created"})
        self.assertEqual(Application.objects.all().count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('facilitator@example.net', mail.outbox[0].cc)
        self.assertEqual(mail.outbox[0].to[0], 'user@mail.com')


    def test_duplicate_signup(self):
        c = Client()
        url = '/api/signup/'
        signup_data = {
            'learning_circle': '1',
            'name': 'User name',
            'email': 'user@mail.com',
            'consent': 'true',
            'communications_opt_in': 'true',
            'mobile': '+12812344321',
            'signup_questions': {
                'goals': 'Learn new stuff',
                'support': 'Help my fellow learners'
            }
        }
        resp = c.post(url, data=json.dumps(signup_data), content_type='application/json')
        resp = c.post(url, data=json.dumps(signup_data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "created"})
        self.assertEqual(Application.objects.all().count(), 1)
        self.assertEqual(len(mail.outbox), 1)


    def test_required_fields(self):
        c = Client()
        url = '/api/signup/'
        signup_data = {
            'learning_circle': '1',
            'name': 'User name',
            'email': 'user@mail.com',
            'consent': 'true',
            'signup_questions': {
                'goals': 'Learn new stuff',
                'support': 'Help my fellow learners'
            }
        }

        # test required fields
        required_fields = ['learning_circle', 'name', 'email', 'consent']
        for field in required_fields:
            data = dict(signup_data)
            del data[field]
            resp = c.post(url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json()['status'], 'error')
            self.assertIn(field, resp.json()['errors'])
            self.assertEqual(Application.objects.all().count(), 0)


    def test_custom_signup_question(self):
        sg = StudyGroup.objects.get(pk=1)
        sg.signup_question = 'This is a mandatory extra question'
        sg.save()
        c = Client()
        url = '/api/signup/'
        signup_data = {
            'learning_circle': '1',
            'name': 'User name',
            'email': 'user@mail.com',
            'consent': 'true',
            'communications_opt_in': 'true',
            'mobile': '+12812344321',
            'signup_questions': {
                'goals': 'Learn new stuff',
                'support': 'Help my fellow learners'
            }
        }
        resp = c.post(url, data=json.dumps(signup_data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('status'), "error")
        self.assertEqual(Application.objects.all().count(), 0)
        self.assertEqual(len(mail.outbox), 0)

        signup_data['signup_questions']['custom_question'] = 'this is my answer'
        resp = c.post(url, data=json.dumps(signup_data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "created"})
        self.assertEqual(Application.objects.all().count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('facilitator@example.net', mail.outbox[0].cc)
        self.assertEqual(mail.outbox[0].to[0], 'user@mail.com')


    def test_invalid_learning_circle(self):
        c = Client()
        url = '/api/signup/'
        signup_data = {
            'learning_circle': '99',
            'name': 'User name',
            'email': 'user@mail.com',
            'consent': 'true',
            'communications_opt_in': 'false',
            'signup_questions': {
                'goals': 'Learn new stuff',
                'support': 'Help my fellow learners',
                'computer_access': 'Both',
                'use_internet': '4' #Expert
            }
        }

        resp = c.post(url, data=json.dumps(signup_data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {
            "status": "error",
            "errors": {"learning_circle": ["No matching learning circle exists"]}
        })
        self.assertEqual(Application.objects.all().count(), 0)
