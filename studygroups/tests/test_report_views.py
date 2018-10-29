# coding: utf-8
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone

from mock import patch

from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import Course
from studygroups.models import accept_application

from surveys.models import LearnerSurveyResponse

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

    def setUp(self):
        user = User.objects.create_user('admin', 'admin@test.com', 'password')
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

    def test_study_group_final_report_with_no_responses(self):
        facilitator = User.objects.create_user('bowie', 'hi@example.net', 'password')
        course_data = dict(
            title='Course 1011',
            provider='CourseMagick',
            link='https://course.magick/test',
            caption='learn by means of magic',
            on_demand=True,
            topics='html,test',
            language='en',
            created_by=facilitator
        )
        course = Course.objects.create(**course_data)
        sg = StudyGroup.objects.get(pk=1)
        sg.course = course
        sg.facilitator = facilitator
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
        self.assertEqual(response.context_data['survey_responses'], 0)
        self.assertNotIn('courses', response.context_data)


    def mock_generate(self, **opts):
        return "image"

    @patch('studygroups.charts.LearnerGoalsChart.generate', mock_generate)
    @patch('studygroups.charts.NewLearnersChart.generate', mock_generate)
    @patch('studygroups.charts.CompletionRateChart.generate', mock_generate)
    @patch('studygroups.charts.GoalsMetChart.generate', mock_generate)
    @patch('studygroups.charts.SkillsLearnedChart.generate', mock_generate)
    @patch('studygroups.charts.ReasonsForSuccessChart.generate', mock_generate)
    @patch('studygroups.charts.NextStepsChart.generate', mock_generate)
    @patch('studygroups.charts.IdeasChart.generate', mock_generate)
    @patch('studygroups.charts.FacilitatorRatingChart.generate', mock_generate)
    @patch('studygroups.charts.LearnerRatingChart.generate', mock_generate)
    @patch('studygroups.charts.PromotionChart.generate', mock_generate)
    @patch('studygroups.charts.LibraryUsageChart.generate', mock_generate)
    @patch('studygroups.charts.AdditionalResourcesChart.generate', mock_generate)
    @patch('studygroups.charts.FacilitatorNewSkillsChart.generate', mock_generate)
    @patch('studygroups.charts.FacilitatorTipsChart.generate', mock_generate)
    def test_study_group_final_report_with_responses(self):
        facilitator = User.objects.create_user('bowie', 'hi@example.net', 'password')
        course_data = dict(
            title='Course 1011',
            provider='CourseMagick',
            link='https://course.magick/test',
            caption='learn by means of magic',
            on_demand=True,
            topics='html,test',
            language='en',
            created_by=facilitator
        )
        course = Course.objects.create(**course_data)
        sg = StudyGroup.objects.get(pk=1)
        sg.course = course
        sg.facilitator = facilitator
        sg.save()

        data = dict(self.APPLICATION_DATA)
        data['study_group'] = sg
        data['email'] = 'mail1@example.net'
        application = Application(**data)
        application.save()
        accept_application(application)

        self.create_learner_survey_response(sg, application)

        c = Client()
        report = '/en/studygroup/{}/report/'.format(sg.pk)
        response = c.get(report)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['study_group'], sg)
        self.assertEqual(response.context_data['registrations'], 1)
        self.assertEqual(response.context_data['survey_responses'], 1)
        self.assertEqual(response.context_data['course'], course)
        self.assertEqual(response.context_data['learner_goals_chart'], "image")
        self.assertEqual(response.context_data['goals_met_chart'], "image")


