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

class TestCourseApi(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    def test_list_all_courses(self):
        c = Client()
        resp = c.get('/api/courses/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 4)
        item_fields = [
            u'learning_circles',
            u'language',
            u'title',
            u'topics',
            u'caption',
            u'link',
            u'provider',
            u'id',
            u'on_demand',
        ]
        resp_keys = resp.json()["items"][0].keys()
        for key in resp_keys:
            self.assertIn(key, item_fields)
        for key in item_fields:
            self.assertIn(key, resp_keys)

    def test_find_by_q(self):
        c = Client()

        # search for a title
        resp = c.get('/api/courses/', {'q': 'Programming with Python'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")
        # search for a topic
        resp = c.get('/api/courses/', {'q': 'uniquetopic1'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")

        # search for a caption
        resp = c.get('/api/courses/', {'q': 'uniquecaption1'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")

        # search for a provider
        resp = c.get('/api/courses/', {'q': 'Khan'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)


    def test_search_by_topics(self):
        c = Client()
        # no matches
        resp = c.get('/api/courses/', {'topics': 'supercalifragilistic'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 0)

        # match 1 topic
        resp = c.get('/api/courses/', {'topics': 'uniquetopic1'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)

        # match 2 different courses
        resp = c.get('/api/courses/', {'topics': 'uniquetopic1,uniquetopic2'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 2)


    def test_search_by_active(self):
        # TODO
        pass
