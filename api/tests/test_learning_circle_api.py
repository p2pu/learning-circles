# coding: utf-8
from django.test import TestCase
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User

from mock import patch

from studygroups.models import StudyGroup

import datetime
import json

class TestLearningCircleApi(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    def setUp(self):
        user = User.objects.create_user('faci@example.net', 'faci@example.net', 'password')
        user.is_superuser = True
        user.is_staff = True
        user.save()


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
            "start_date": "2018-02-12",
            "weeks": 2,
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC"
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "created"})
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(lc.course.id, 3)
        self.assertEqual(lc.description, 'Lets learn something')
        self.assertEqual(lc.start_date, datetime.date(2018,2,12))
        self.assertEqual(lc.meeting_time, datetime.time(17,1))
        self.assertEqual(lc.studygroupmeeting_set.all().count(), 2)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, 'Your Learning Circle has been created! What next?')
        self.assertIn('faci@example.net', mail.outbox[0].to)
        self.assertIn('community@localhost', mail.outbox[0].bcc)


    def test_get_learning_circles(self):
        c = Client()
        resp = c.get('/api/learningcircles/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 4)


    def test_get_learning_circles_by_weekday(self):
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2018,01,26)
        sg.save()
        sg = StudyGroup.objects.get(pk=2)
        sg.start_date = datetime.date(2018,01,27)
        sg.save()
        c = Client()
        # Friday and Saturday   
        resp = c.get('/api/learningcircles/?weekdays=4,5')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 2)

