# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language
from django.urls import reverse
from django.conf import settings

from unittest.mock import patch
from freezegun import freeze_time

from studygroups.models import StudyGroup
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models.device_allocation import DeviceAllocation
from studygroups.models.device_allocation import check_user_device_allocation
from custom_registration.models import create_user

import datetime
import urllib.request, urllib.parse, urllib.error
import json



"""
Tests for when facilitators interact with the system
"""
class TestFacilitatorViews(TestCase):

    fixtures = ['test_teams.json', 'test_courses.json', 'test_studygroups.json']

    def setUp(self):
        with patch('custom_registration.signals.send_email_confirm_email'):
            user = create_user('bob@example.net', 'bob', 'test', 'password')
            # Assign user to team
            team = Team.objects.create(name='test team', page_slug='digital-detroit')
            TeamMembership.objects.create(team=team, user=user, role=TeamMembership.MEMBER)
            self.facilitator = user

        mailchimp_patcher = patch('studygroups.models.profile.update_mailchimp_subscription')
        self.mock_maichimp = mailchimp_patcher.start()
        self.addCleanup(mailchimp_patcher.stop)


    def test_create_study_group_with_limit(self):
        self.assertEquals(1, DeviceAllocation.objects.count())
        DeviceAllocation.objects.all().delete()
        c = Client()
        c.login(username='bob@example.net', password='password')
        data = {
            "name": "Test learning circle",
            "course": 3,
            "description": "Lets learn something",
            "course_description": "A real great course",
            "venue_name": "75 Harrington",
            "venue_details": "top floor",
            "venue_address": "75 Harrington",
            "city": "Cape Town",
            "country": "South Africa",
            "country_en": "South Africa",
            "region": "Western Cape",
            "latitude": 3.1,
            "longitude": "1.3",
            "place_id": "1",
            "online": "false",
            "language": "en",
            "meetings": [
                { "meeting_date": "2026-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2026-02-19", "meeting_time": "17:01" },
            ],
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png",
            "facilitator_concerns": "blah blah",
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)

        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.json(), {
            "status": "error",
            'errors': {
                'signup_limit': [
                    'You need to specify a signup limit for this learning circle less than or equal to 0',
                ],
            },
        })

        DeviceAllocation.objects.create(user=self.facilitator, start_date=datetime.date(2026,1,1), cutoff_date=datetime.date(2027,1,1), amount=20)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)


        self.assertEqual(resp.json(), {
            "status": "error",
            'errors': {
                'signup_limit': [
                    'You need to specify a signup limit for this learning circle less than or equal to 20',
                ],
            },
        })

        data['signup_limit'] = 12
        resp = c.post(url, data=json.dumps(data), content_type='application/json')

        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {
            "status": "created",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })

        self.assertEqual(StudyGroup.objects.all().count(), 5)

        self.assertEqual(check_user_device_allocation(self.facilitator, datetime.date(2026,2,2)), 8)


    def test_update_learning_circle(self):
        self.assertEquals(1, DeviceAllocation.objects.count())
        DeviceAllocation.objects.all().delete()

        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()

        c = Client()
        c.login(username='bob@example.net', password='password')
        data = {
            "course": 3,
            "description": "Lets learn something",
            "course_description": "A real great course",
            "venue_name": "75 Harrington",
            "venue_details": "top floor",
            "venue_address": "75 Harrington",
            "city": "Cape Town",
            "country": "South Africa",
            "country_en": "South Africa",
            "region": "Western Cape",
            "latitude": 3.1,
            "longitude": "1.3",
            "place_id": "4",
            "online": "false",
            "language": "en",
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png",
            "draft": False,
            "meetings": [
                { "meeting_date": "2026-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2026-02-19", "meeting_time": "17:01" },
            ],
            "signup_limit": 20,
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        DeviceAllocation.objects.create(user=self.facilitator, start_date=datetime.date(2026,1,1), cutoff_date=datetime.date(2027,1,1), amount=20)


        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(check_user_device_allocation(self.facilitator, datetime.date(2026,2,2)), 0)

        # Update learning circle
        lc = StudyGroup.objects.all().last()
        self.assertFalse(lc.draft)
        url = '/api/learning-circle/{}/'.format(lc.pk)
        data["facilitators"] = [f.user_id for f in lc.facilitator_set.all()]
        data["signup_limit"] = 21

        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'error')

        data["signup_limit"] = 19
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {
            "status": "updated",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })
        self.assertEqual(check_user_device_allocation(self.facilitator, datetime.date(2026,2,2)), 1)

