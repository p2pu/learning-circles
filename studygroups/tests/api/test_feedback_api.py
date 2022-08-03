# coding: utf-8
from django.test import TestCase, RequestFactory
from django.test import Client
from django.core import mail
from django.utils import timezone
from django.conf import settings

from unittest.mock import patch
from freezegun import freeze_time

from studygroups.models import generate_all_meetings
from studygroups.models import StudyGroup
from studygroups.models import Profile
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import Meeting
from studygroups.models import Feedback
from studygroups.views import LearningCircleListView
from custom_registration.models import create_user
from django.contrib.auth.models import User


import datetime
import json


class TestFeedbackApi(TestCase):

    fixtures = ['test_teams.json', 'test_courses.json', 'test_studygroups.json']

    def setUp(self):
        with patch('custom_registration.signals.send_email_confirm_email'):
            user = create_user('faci@example.net', 'b', 't', 'password', False)
            user.save()
            self.facilitator = user
        sg = StudyGroup.objects.get(pk=1)
        sg.created_by = user
        sg.save()

        meeting = Meeting()
        meeting.study_group = sg
        meeting.meeting_time = timezone.now().time()
        meeting.meeting_date = timezone.now().date() - datetime.timedelta(days=1)
        meeting.save()
        self.meeting = meeting


    def test_feedback_permissions(self):
        c = Client()
        data = {
            "study_group_meeting": self.meeting.pk,
            "rating": 3,
        }
        url = '/api/drf/meeting_feedback/'

        def assertForbidden(resp):
            self.assertEqual(resp.status_code, 403)

        # not logged in
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        assertForbidden(resp)

        # wrong facilitator
        user = create_user('bob@example.net', 'bob', 'test', 'password')
        c.login(username='bob@example.net', password='password')
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        assertForbidden(resp)

        # how about now?
        c.login(username=self.facilitator.username, password='password')
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Feedback.objects.filter(study_group_meeting=self.meeting).count(), 1)

