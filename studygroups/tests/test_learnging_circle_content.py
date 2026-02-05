# coding: utf-8
from django.test import TestCase
from django.test import Client

from unittest.mock import patch

from studygroups.models import Facilitator
from studygroups.models import StudyGroup
from custom_registration.models import create_user
from courses import models as course_model
from content import models as content_model


"""
Tests for when facilitators interact with the system
"""
class TestLearningCircleContentViews(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    APPLICATION_DATA = {
        'study_group': '1',
        'name': 'Test User',
        'email': 'test@mail.com',
        'mobile': '',
        'goals': 'Social reasons',
        'support': 'thinking how to?',
        'computer_access': 'Both',
        'consent': True,
        'use_internet': '2'
    }

    STUDY_GROUP_DATA = {
        'course': '1',
        'name': "Motorcycles FTW",
        'venue_name': 'мой дом',
        'venue_details': 'Garrage at my house',
        'venue_address': 'Rosemary Street 6',
        'city': 'Johannesburg',
        'country': 'South Africa',
        'country_en': 'South Africa',
        'region': 'Gauteng',
        'latitude': -26.205,
        'longitude': 28.0497,
        'place_id': '342432',
        'language': 'en',
        'description': 'We will complete the course about motorcycle maintenance together',
        'start_date': '2018-07-25',
        'weeks': '6',
        'meeting_time': '19:00',
        'duration': '90',
        'timezone': 'Africa/Johannesburg',
        'facilitator_concerns': 'how do i market',
        'venue_website': 'http://venue.com',
        'meetings': [
            { "meeting_date": "2018-07-25", "meeting_time": "19:00" },
            { "meeting_date": "2018-08-01", "meeting_time": "16:00" },
            { "meeting_date": "2018-08-08", "meeting_time": "16:00" },
            { "meeting_date": "2018-08-15", "meeting_time": "16:00" },
            { "meeting_date": "2018-08-22", "meeting_time": "16:00" },
            { "meeting_date": "2018-08-29", "meeting_time": "16:00" },
        ]
    }

    def setUp(self):
        patcher = patch('studygroups.views.learner.requests.post')
        self.mock_captcha = patcher.start()
        self.mock_captcha.json.return_value = {"success": True}
        self.addCleanup(patcher.stop)

        mailchimp_patcher = patch('studygroups.models.profile.update_mailchimp_subscription')
        self.mock_maichimp = mailchimp_patcher.start()
        self.addCleanup(mailchimp_patcher.stop)


        user = create_user('admin@test.com', 'admin', 'admin', 'password')
        user.is_superuser = True
        user.is_staff = True
        user.save()



    def test_facilitator_access(self):
        # Course with content
        course = course_model.create_course(
            **{
                "title": 'Course with content',
                "hashtag": '#hashtag',
                "description": "Some wordy description of this course",
                "language": "en",
                "organizer_uri": '/uri/users/bob',
            }
        )
        content = content_model.create_content('title', 'content', '/uri/users/bob')
        course_model.add_course_content(course['uri'], content['uri'])


        user = create_user('bob@example.net', 'bob', 'test', 'password')
        # StudyGroup based on Course
        sg = StudyGroup.objects.get(pk=1)
        sg.course_content_id = course['id']
        sg.save()

        c = Client()
        c.login(username='bob@example.net', password='password')

        # test no access as facilitator
        url = f'/en/studygroup/{sg.id}/content/{content["id"]}/'
        resp = c.get(url)
        self.assertRedirects(resp, '/en/signup/harold-washington-1/')

        Facilitator.objects.create(study_group=sg, user=user)

        url = f'/en/studygroup/{sg.id}/content/{content["id"]}/'
        resp = c.get(url)
        self.assertEqual(resp.status_code, 200)

        # test that sneakiness doesn't work
        other_content = content_model.create_content('title', 'content', '/uri/users/bob')
        url = f'/en/studygroup/{sg.id}/content/{other_content["id"]}/'
        resp = c.get(url)
        self.assertNotEqual(resp.status_code, 200)

