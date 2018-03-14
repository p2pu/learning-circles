# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language

from mock import patch

from studygroups.models import StudyGroup
from studygroups.models import Application

import datetime
import json

class TestApiSignupView(TestCase):

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


    def test_valid_signup(self):
        c = Client()
        url = '/api/signup/'
        signup_data = {
            'study_group': '1',
            'name': 'User name',
            'email': 'user@mail.com',
            'mobile': '+12812344321',
            'signup_questions': {
                'goals': 'Learn new stuff',
                'support': 'Help my fellow learners',
                'computer_access': 'Both',
                'use_internet': '4' #Expert
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
            'study_group': '1',
            'name': 'User name',
            'email': 'user@mail.com',
            'mobile': '+12812344321',
            'signup_questions': {
                'goals': 'Learn new stuff',
                'support': 'Help my fellow learners',
                'computer_access': 'Both',
                'use_internet': '4' #Expert
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
            'study_group': '1',
            'name': 'User name',
            'email': 'user@mail.com',
            'signup_questions': {
                'goals': 'Learn new stuff',
                'support': 'Help my fellow learners',
                'computer_access': 'Both',
                'use_internet': '4' #Expert
            }
        }

        # test required fields
        required_fields = ['study_group', 'name', 'email']
        for field in required_fields:
            data = dict(signup_data)
            del data[field]
            resp = c.post(url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json()['status'], 'error')
            self.assertIn(field, resp.json()['errors'])
            self.assertEqual(Application.objects.all().count(), 0)


    def test_invalid_learning_circle(self):
        c = Client()
        url = '/api/signup/'
        signup_data = {
            'study_group': '99',
            'name': 'User name',
            'email': 'user@mail.com',
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
            "errors": {"study_group": ["No matching learning circle exists"]}
        })
        self.assertEqual(Application.objects.all().count(), 0)
