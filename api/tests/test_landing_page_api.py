# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language

from mock import patch
from freezegun import freeze_time

from studygroups.models import StudyGroup
from studygroups.models import Meeting

import datetime
import json

class TestCourseApi(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    def test_landing_page_learning_circles(self):
        c = Client()
        meeting_1 = Meeting.objects.create(
            study_group_id=1,
            meeting_date=datetime.date(2017,10,25),
            meeting_time=datetime.time(17,30),
        )
        meeting_2 = Meeting.objects.create(
            study_group_id=2,
            meeting_date=datetime.date(2017,10,26),
            meeting_time=datetime.time(17,30),
        )
        meeting_3 = Meeting.objects.create(
            study_group_id=3,
            meeting_date=datetime.date(2017,10,27),
            meeting_time=datetime.time(17,30),
        )
        meeting_4 = Meeting.objects.create(
            study_group_id=4,
            meeting_date=datetime.date(2017,10,31),
            meeting_time=datetime.time(17,30),
        )

        with freeze_time("2017-10-24 17:55:34"):
            resp = c.get('/api/landing-page-learning-circles/')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()["items"]), 3)

        with freeze_time("2017-10-25 17:55:34"):
            resp = c.get('/api/landing-page-learning-circles/')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()["items"]), 3)

        with freeze_time("2017-10-31 17:55:34"):
            resp = c.get('/api/landing-page-learning-circles/')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()["items"]), 3)

        with freeze_time("2017-11-30 17:55:34"):
            resp = c.get('/api/landing-page-learning-circles/')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(resp.json()["items"]), 3)
