# coding: utf-8
from django.test import TestCase
from django.test import Client
from django.core import mail
from django.utils import timezone

from mock import patch

from studygroups.models import StudyGroup
from custom_registration.models import create_user

import datetime
import json

class TestLearningCircleApi(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    def setUp(self):
        with patch('custom_registration.signals.send_email_confirm_email'):
            user = create_user('faci@example.net', 'b', 't', 'password', False)
            user.save()
            self.facilitator = user


    def test_create_learning_circle(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
        data = {
            "course": 3,
            "description": "Lets learn something",
            "venue_name": "75 Harrington",
            "venue_details": "top floor",
            "venue_address": "75 Harrington",
            "city": "Cape Town",
            "latitude": 3.1,
            "longitude": "1.3",
            "place_id": 1,
            "start_date": "2018-02-12",
            "weeks": 2,
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png"
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "url": "example.net/en/signup/75-harrington-{}/".format(lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.course.id, 3)
        self.assertEqual(lc.description, 'Lets learn something')
        self.assertEqual(lc.start_date, datetime.date(2018,2,12))
        self.assertEqual(lc.meeting_time, datetime.time(17,1))
        self.assertEqual(lc.meeting_set.all().count(), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your Learning Circle has been created! What next?')
        self.assertIn('faci@example.net', mail.outbox[0].to)
        self.assertIn('community@localhost', mail.outbox[0].cc)


    def test_create_learning_circle_and_publish(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()
        data = {
            "course": 3,
            "description": "Lets learn something",
            "venue_name": "75 Harrington",
            "venue_details": "top floor",
            "venue_address": "75 Harrington",
            "city": "Cape Town",
            "latitude": 3.1,
            "longitude": "1.3",
            "place_id": 1,
            "start_date": "2018-02-12",
            "weeks": 2,
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png",
            "draft": False,
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "url": "example.net/en/signup/75-harrington-{}/".format(lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.course.id, 3)
        self.assertEqual(lc.draft, False)
        self.assertEqual(lc.description, 'Lets learn something')
        self.assertEqual(lc.start_date, datetime.date(2018,2,12))
        self.assertEqual(lc.meeting_time, datetime.time(17,1))
        self.assertEqual(lc.meeting_set.all().count(), 2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your Learning Circle has been created! What next?')
        self.assertIn('faci@example.net', mail.outbox[0].to)
        self.assertIn('community@localhost', mail.outbox[0].cc)


    def test_create_learning_circle_and_publish_user_unconfirmed(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
        data = {
            "course": 3,
            "description": "Lets learn something",
            "venue_name": "75 Harrington",
            "venue_details": "top floor",
            "venue_address": "75 Harrington",
            "city": "Cape Town",
            "latitude": 3.1,
            "longitude": "1.3",
            "start_date": "2018-02-12",
            "weeks": 2,
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png",
            "draft": False,
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json().get('status'), 'created')
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(StudyGroup.objects.last().draft, True)
        self.assertEqual(len(mail.outbox), 1)


    def test_update_learning_circle(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
        data = {
            "course": 3,
            "description": "Lets learn something",
            "venue_name": "75 Harrington",
            "venue_details": "top floor",
            "venue_address": "75 Harrington",
            "city": "Cape Town",
            "latitude": 3.1,
            "longitude": "1.3",
            "place_id": 4,
            "start_date": "2018-02-12",
            "weeks": 2,
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png"
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "url": "example.net/en/signup/75-harrington-{}/".format(lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        data['start_date'] = '2018-01-01'
        data['course'] = 1
        # Update learning circle
        url = '/api/learning-circle/{}/'.format(lc.pk)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json()['status'], 'updated')
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.start_date, datetime.date(2018, 1, 1))
        self.assertEqual(lc.course.id, 1)


    def test_publish_learning_circle(self):
        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()
        c = Client()
        c.login(username='faci@example.net', password='password')
        data = {
            "course": 3,
            "description": "Lets learn something",
            "venue_name": "75 Harrington",
            "venue_details": "top floor",
            "venue_address": "75 Harrington",
            "city": "Cape Town",
            "latitude": 3.1,
            "longitude": "1.3",
            "place_id": 4,
            "start_date": "2018-02-12",
            "weeks": 2,
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png"
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "url": "example.net/en/signup/75-harrington-{}/".format(lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.meeting_set.all().count(), 0)
        data['draft'] = False
        # Update learning circle
        url = '/api/learning-circle/{}/'.format(lc.pk)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json()['status'], 'updated')
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.meeting_set.all().count(), 2)


    def test_get_learning_circles(self):
        c = Client()
        resp = c.get('/api/learningcircles/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 4)


    def test_get_learning_circles_unicode(self):
        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()
        c = Client()
        c.login(username='faci@example.net', password='password')
        data = {
            "course": 3,
            "description": "Lets learn something",
            "venue_name": "الصحة النفسية للطفل",
            "venue_details": "top floor",
            "venue_address": "75 Harrington",
            "city": "Cape Town",
            "latitude": 3.1,
            "longitude": "1.3",
            "place_id": 4,
            "start_date": "2018-02-12",
            "weeks": 2,
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png",
            "draft": False,
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "url": "example.net/en/signup/75-harrington-{}/".format(lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)


        c = Client()
        resp = c.get('/api/learningcircles/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 5)


    def test_get_learning_circles_exclude_drafts(self):
        c = Client()
        sg = StudyGroup.objects.get(pk=1)
        sg.draft = True
        sg.save()
        resp = c.get('/api/learningcircles/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 3)


    def test_get_learning_circles_by_weekday(self):
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2018,1,26)
        sg.save()
        sg = StudyGroup.objects.get(pk=2)
        sg.start_date = datetime.date(2018,1,27)
        sg.save()
        c = Client()
        # Friday and Saturday   
        resp = c.get('/api/learningcircles/?weekdays=4,5')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 2)

