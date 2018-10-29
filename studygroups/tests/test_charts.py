# # coding: utf-8
# from django.test import TestCase
# from django.test import Client
# from django.utils import timezone

# from mock import patch

# from studygroups import charts
# from studygroups.models import StudyGroup
# from studygroups.models import Meeting
# from studygroups.models import Application
# from surveys.models import LearnerSurveyResponse
# from surveys.models import FacilitatorSurveyResponse

# import json


# # Things to test:
# # - get_question_field and get_response_field retrieve correct json or None
# # - save_image hits AWS api and returns url
# # - for each chart:
# #     - correct pygal chart object is instantiated
# #     - get_data returns data in correct format
# #     - get_data calls get_response_field with the right typeform question ID
# #     - generate function outputs svg if called with no args and <img> if called with "png"
# #     - "no data" is returned if there's no data


# class TestCharts(TestCase):
