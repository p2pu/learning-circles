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
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import Course
from studygroups.models import TopicGuide
from custom_registration.models import create_user

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
            'learning_circles',
            'language',
            'language_display',
            'title',
            'keywords',
            'topics',
            'format',
            'caption',
            'link',
            'provider',
            'id',
            'on_demand',
            'platform',
            'creator',
            'overall_rating',
            'total_ratings',
            'rating_step_counts',
            'course_page_url',
            'course_page_path',
            'course_edit_path',
            'created_at',
            'unlisted',
        ]
        resp_keys = list(resp.json()["items"][0].keys())
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
        topic_guide = TopicGuide.objects.create(title='Topic 1', slug='topic-1')
        resp = c.get('/api/courses/', {'topics': 'topic-1'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 0)

        # match 1 topic
        Course.objects.get(pk=1).topic_guides.add(topic_guide)
        resp = c.get('/api/courses/', {'topics': 'topic-1'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)


    def test_find_by_q_incremental(self):
        c = Client()

        # search for a title
        resp = c.get('/api/courses/', {'q': 'Pro'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")

        resp = c.get('/api/courses/', {'q': 'pyth'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")

        resp = c.get('/api/courses/', {'q': 'prog'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")

        resp = c.get('/api/courses/', {'q': 'progr'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")

        resp = c.get('/api/courses/', {'q': 'progra'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")

        resp = c.get('/api/courses/', {'q': 'program'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")

        resp = c.get('/api/courses/', {'q': 'programm'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")

        resp = c.get('/api/courses/', {'q': 'programmin'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")

        resp = c.get('/api/courses/', {'q': 'programming'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(resp.json()["items"][0]["title"], "Programming with Python")


    def test_search_by_active(self):
        # TODO
        pass


    def test_team_unlisted(self):
        c = Client()

        # create team with 2 users
        organizer = create_user('organ@team.com', 'organ', 'test', '1234', False)
        faci1 = create_user('faci1@team.com', 'faci1', 'test', '1234', False)
        StudyGroup.objects.filter(pk=1).update(created_by=faci1)
        mail.outbox = []

        # create team
        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        TeamMembership.objects.create(team=team, user=faci1, role=TeamMembership.MEMBER)

        # add some courses
        self.assertEqual(Course.objects.count(), 4)
        Course.objects.filter(pk=1).update(created_by=faci1)
        Course.objects.filter(pk=2).update(created_by=faci1)
        Course.objects.filter(pk=3).update(created_by=organizer)
        Course.objects.filter(pk=4).update(created_by=faci1)

        # unlist some
        Course.objects.filter(pk=1).update(unlisted=True)

        # test that when logged out, only listed are shown
        resp = c.get('/api/courses/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 3)

        # test when logged in as any team member, unlisted are also shown
        c.login(username='faci1@team.com', password='1234')
        resp = c.get('/api/courses/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 4)
