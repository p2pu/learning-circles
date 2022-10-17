# coding: utf-8
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

from unittest.mock import patch

from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import Course
from studygroups.models import accept_application
from custom_registration.models import create_user

from surveys.models import LearnerSurveyResponse
from surveys.models import FacilitatorSurveyResponse

import datetime
import json


"""
Tests for when organizers interact with the system
"""
class TestReportViews(TestCase):
    fixtures = ['test_courses.json', 'test_studygroups.json']

    APPLICATION_DATA = {
        'name': 'Test User',
        'email': 'test@mail.com',
        'signup_questions': json.dumps({
            'computer_access': 'Yes',
            'goals': 'try hard',
            'support': 'thinking how to?',
        }),
        'study_group': '1',
    }

    def mock_generate(self, **opts):
        return "image"

    def setUp(self):
        user = create_user('admin@test.com', 'admin', 'smadmin', 'password')
        user.is_superuser = True
        user.is_staff = True
        user.save()

    def create_learner_survey_response(self, study_group, learner):
        survey_data = dict(
            typeform_key="123",
            study_group=study_group,
            learner=learner,
            survey="[]",
            response="[]",
            responded_at=timezone.now()
        )
        return LearnerSurveyResponse.objects.create(**survey_data)

    def create_facilitator_survey_response(self, study_group):
        survey_data = dict(
            typeform_key="123",
            study_group=study_group,
            survey="[]",
            response="[]",
            responded_at=timezone.now()
        )
        return FacilitatorSurveyResponse.objects.create(**survey_data)

    def test_study_group_final_report_with_no_responses(self):
        facilitator = create_user('hi@example.net', 'bowie', 'wowie', 'password')
        course_data = dict(
            title='Course 1011',
            provider='CourseMagick',
            link='https://course.magick/test',
            caption='learn by means of magic',
            on_demand=True,
            keywords='html,test',
            language='en',
            created_by=facilitator
        )
        course = Course.objects.create(**course_data)
        sg = StudyGroup.objects.get(pk=1)
        sg.course = course
        sg.created_by = facilitator
        sg.save()

        data = dict(self.APPLICATION_DATA)
        data['study_group'] = sg
        data['email'] = 'mail1@example.net'
        application = Application(**data)
        application.save()
        accept_application(application)

        c = Client()
        report = '/en/studygroup/{}/report/'.format(sg.pk)
        response = c.get(report)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['study_group'], sg)
        self.assertEqual(response.context_data['registrations'], 1)
        self.assertEqual(response.context_data['learner_survey_responses'], 0)
        self.assertEqual(response.context_data['facilitator_survey_responses'], 0)
        self.assertNotIn('courses', response.context_data)


    def test_study_group_final_report_with_only_facilitator_response(self):
        # TODO
        return
        facilitator = create_user('hi@example.net', 'bowie', 'wowie', 'password')
        course_data = dict(
            title='Course 1011',
            provider='CourseMagick',
            link='https://course.magick/test',
            caption='learn by means of magic',
            on_demand=True,
            keywords='html,test',
            language='en',
            created_by=facilitator
        )
        course = Course.objects.create(**course_data)
        sg = StudyGroup.objects.get(pk=1)
        sg.course = course
        sg.created_by = facilitator
        sg.save()

        data = dict(self.APPLICATION_DATA)
        data['study_group'] = sg
        data['email'] = 'mail1@example.net'
        application = Application(**data)
        application.save()
        accept_application(application)

        self.create_facilitator_survey_response(sg)

        c = Client()
        report = reverse('studygroups_final_report', kwargs={'study_group_id': sg.pk })
        response = c.get(report)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['study_group'], sg)
        self.assertEqual(response.context_data['registrations'], 1)
        self.assertEqual(response.context_data['learner_survey_responses'], 0)
        self.assertEqual(response.context_data['facilitator_survey_responses'], 1)
        self.assertEqual(response.context_data['course'], course)
        self.assertEqual(response.context_data['goals_met_chart'], "image")


    def test_study_group_final_report_with_responses(self):
        # TODO
        return
        facilitator = create_user('hi@example.net', 'bowie', 'wowie', 'password')
        course_data = dict(
            title='Course 1011',
            provider='CourseMagick',
            link='https://course.magick/test',
            caption='learn by means of magic',
            on_demand=True,
            keywords='html,test',
            language='en',
            created_by=facilitator
        )
        course = Course.objects.create(**course_data)
        sg = StudyGroup.objects.get(pk=1)
        sg.course = course
        sg.created_by = facilitator
        sg.save()

        data = dict(self.APPLICATION_DATA)
        data['study_group'] = sg
        data['email'] = 'mail1@example.net'
        application = Application(**data)
        application.save()
        accept_application(application)

        self.create_learner_survey_response(sg, application)

        c = Client()
        report = reverse('studygroups_final_report', kwargs={'study_group_id': sg.pk })
        response = c.get(report)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['study_group'], sg)
        self.assertEqual(response.context_data['registrations'], 1)
        self.assertEqual(response.context_data['learner_survey_responses'], 1)
        self.assertEqual(response.context_data['facilitator_survey_responses'], 0)
        self.assertEqual(response.context_data['course'], course)
        self.assertEqual(response.context_data['goals_met_chart'], "image")


    @patch('studygroups.charts.LearningCircleMeetingsChart.generate')
    @patch('studygroups.charts.LearningCircleCountriesChart.generate')
    @patch('studygroups.charts.TopTopicsChart.generate')
    def test_community_digest(self, topics_chart_generate, countries_chart_generate, meetings_chart_generate):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        start_date = end_date - datetime.timedelta(days=21)

        c = Client()
        community_digest = reverse('studygroups_community_digest', kwargs={'start_date': start_date.strftime("%d-%m-%Y"), 'end_date': end_date.strftime("%d-%m-%Y")})
        response = c.get(community_digest)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['web'], True)
        self.assertIsNotNone(response.context_data['meetings_chart'])
        self.assertIsNotNone(response.context_data['countries_chart'])
        self.assertIsNotNone(response.context_data['top_topics_chart'])
        topics_chart_generate.assert_called()
        countries_chart_generate.assert_called()
        meetings_chart_generate.assert_called()

