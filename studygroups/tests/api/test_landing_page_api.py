# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.conf import settings
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language

from mock import patch
from freezegun import freeze_time

from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application

from surveys.models import LearnerSurveyResponse

import datetime
import json

class TestLandingPageApi(TestCase):

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


    def test_learning_circles_map_view(self):
        c = Client()

        active_studygroup = StudyGroup.objects.get(pk=1)
        active_studygroup.end_date = datetime.date(2017,3,23)
        active_studygroup.save()

        finished_studygroup = StudyGroup.objects.get(pk=2)
        learner = Application.objects.create(study_group=finished_studygroup)
        learner_survey_response = LearnerSurveyResponse.objects.create(
            study_group=finished_studygroup,
            learner=learner,
            responded_at=datetime.date(2017,2,23)
        )

        with freeze_time("2017-3-20 17:55:34"):
            response = c.get('/api/learning-circles-map/')
            data = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data["items"]), 4)

            active_item = next(item for item in data["items"] if item["id"] == active_studygroup.id)
            self.assertEqual(active_item["active"], True)
            self.assertEqual(active_item, {
                'active': True,
                'city': 'Chicago',
                'id': 1,
                'latitude': '41.850030',
                'longitude': '-87.650050',
                'start_date': '2015-03-23',
                'title': 'Test learning circle',
                'url': settings.PROTOCOL + '://' + settings.DOMAIN + '/en/signup/harold-washington-1/'
            })

            finished_item = next(item for item in data["items"] if item["id"] == finished_studygroup.id)
            self.assertEqual(finished_item, {
                'active': False,
                'city': 'Chicago',
                'id': 2,
                "latitude" : "41.850030",
                "longitude" : "-87.650050",
                'report_url': settings.PROTOCOL + '://' + settings.DOMAIN + '/en/studygroup/2/report/',
                'start_date': '2015-03-23',
                'title': 'The Riders',
            })

            other_item = next(item for item in data["items"] if item["id"] == 4)
            self.assertEqual(other_item, {
                'active': False,
                'city': 'Chicago',
                'id': 4,
                'latitude': '41.850030',
                'longitude': '-87.650050',
                'start_date': '2015-03-23',
                'title': "The Bandits of Hell's Bend"
            })
