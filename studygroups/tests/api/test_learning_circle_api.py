# coding: utf-8
from django.test import TestCase, RequestFactory
from django.test import Client
from django.core import mail
from django.utils import timezone
from django.conf import settings

from unittest.mock import patch
from freezegun import freeze_time

from studygroups.models import StudyGroup
from studygroups.models import Profile
from studygroups.models import Course
from studygroups.models import generate_all_meetings
from studygroups.models import generate_all_meeting_dates
from studygroups.models import generate_meetings_from_dates
from studygroups.models import Team, TeamMembership
from studygroups.views import LearningCircleListView
from custom_registration.models import create_user
from django.contrib.auth.models import User


import datetime
import json

class TestLearningCircleApi(TestCase):

    fixtures = ['test_teams.json', 'test_courses.json', 'test_studygroups.json']

    def setUp(self):
        with patch('custom_registration.signals.send_email_confirm_email'):
            user = create_user('faci@example.net', 'b', 't', 'password', False)
            user.save()
            self.facilitator = user

        mailchimp_patcher = patch('studygroups.models.profile.update_mailchimp_subscription')
        self.mock_maichimp = mailchimp_patcher.start()
        self.addCleanup(mailchimp_patcher.stop)


    def test_create_learning_circle(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
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
                { "meeting_date": "2018-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2018-02-19", "meeting_time": "17:01" },
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

        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.course.id, 3)
        self.assertEqual(lc.name, "Test learning circle")
        self.assertEqual(lc.description, 'Lets learn something')
        self.assertEqual(lc.course_description, 'A real great course')
        self.assertEqual(lc.start_date, datetime.date(2018,2,12))
        self.assertEqual(lc.meeting_time, datetime.time(17,1))
        self.assertEqual(lc.meeting_set.all().count(), 2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your “{}” learning circle in {} has been created!'.format(lc.name, lc.city))
        self.assertIn('faci@example.net', mail.outbox[0].to)
        self.assertIn('community@localhost', mail.outbox[0].cc)


    def test_create_learning_circle_without_name_or_course_description(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
        data = {
            "course": 3,
            "description": "Lets learn something",
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
                { "meeting_date": "2018-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2018-02-19", "meeting_time": "17:01" },
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

        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.name, lc.course.title)
        self.assertEqual(lc.course_description, lc.course.caption)


    @freeze_time('2018-01-20')
    def test_create_learning_circle_and_publish(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()
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
            "facilitator_concerns": "blah blah",
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png",
            "draft": False,
            "meetings": [
                { "meeting_date": "2018-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2018-02-19", "meeting_time": "17:01" },
            ],
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.course.id, 3)
        self.assertEqual(lc.draft, False)
        self.assertEqual(lc.name, "Test learning circle")
        self.assertEqual(lc.description, 'Lets learn something')
        self.assertEqual(lc.course_description, 'A real great course')
        self.assertEqual(lc.start_date, datetime.date(2018,2,12))
        self.assertEqual(lc.meeting_time, datetime.time(17,1))
        self.assertEqual(lc.meeting_set.all().count(), 2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your “{}” learning circle in {} has been created!'.format(lc.name, lc.city))
        self.assertIn('faci@example.net', mail.outbox[0].to)
        self.assertIn('community@localhost', mail.outbox[0].cc)


    @freeze_time('2018-01-20')
    def test_create_learning_circle_and_publish_user_unconfirmed(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
        data = {
            "name": "Storytelling with Sharon",
            "course": 3,
            "course_description": "A real great course",
            "description": "Lets learn something",
            "venue_name": "75 Harrington",
            "venue_details": "top floor",
            "venue_address": "75 Harrington",
            "city": "Cape Town",
            "country": "South Africa",
            "country_en": "South Africa",
            "region": "Western Cape",
            "latitude": 3.1,
            "longitude": "1.3",
            "language": "en",
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png",
            "draft": False,
            "meetings": [
                { "meeting_date": "2018-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2018-02-19", "meeting_time": "17:01" },
            ],
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json().get('status'), 'created')
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(StudyGroup.objects.last().draft, True)
        self.assertEqual(len(mail.outbox), 1)


    def test_create_learning_circle_welcome(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
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
            "place_id": "1",
            "online": "false",
            "language": "en",
            "meeting_time": "17:01",
            "duration": 50,
            "timezone": "UTC",
            "image": "/media/image.png",
            "meetings": [
                { "meeting_date": "2018-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2018-02-19", "meeting_time": "17:01" },
            ],
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)

        # Test without concern only p2pu should be CC-ed
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.course.id, 3)
        self.assertEqual(lc.description, 'Lets learn something')
        self.assertEqual(lc.start_date, datetime.date(2018,2,12))
        self.assertEqual(lc.meeting_time, datetime.time(17,1))
        self.assertEqual(lc.meeting_set.all().count(), 2)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your “{}” learning circle in {} has been created!'.format(lc.name, lc.city))
        self.assertIn('faci@example.net', mail.outbox[0].to)
        self.assertIn('thepeople@p2pu.org', mail.outbox[0].cc)
        self.assertEqual(len(mail.outbox[0].cc), 1)

        # Test with concern - welcome committee should be cc-ed
        mail.outbox = []
        data['facilitator_concerns'] = 'How should I advertise'
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your “{}” learning circle in {} has been created!'.format(lc.name, lc.city))
        self.assertIn('faci@example.net', mail.outbox[0].to)
        self.assertIn('thepeople@p2pu.org', mail.outbox[0].cc)
        self.assertIn('community@localhost', mail.outbox[0].cc)
        self.assertIn(data['facilitator_concerns'], mail.outbox[0].body)
        self.assertEqual(len(mail.outbox[0].cc), 2)

        # Test as part of team with concern - organizer and welcome should be CC-ed
        team = Team.objects.create(name='awesome team')
        team.save()
        organizer = create_user('org@niz.er', 'organ', 'izer', 'passowrd', False)
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        TeamMembership.objects.create(team=team, user=self.facilitator, role=TeamMembership.MEMBER)

        mail.outbox = []
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your “{}” learning circle in {} has been created!'.format(lc.name, lc.city))
        self.assertIn('faci@example.net', mail.outbox[0].to)
        self.assertIn('thepeople@p2pu.org', mail.outbox[0].cc)
        self.assertIn('community@localhost', mail.outbox[0].cc)
        self.assertIn('org@niz.er', mail.outbox[0].cc)
        self.assertEqual(len(mail.outbox[0].cc), 3)

        # Test as part of team - team organizer should be cc-ed
        mail.outbox = []
        del data['facilitator_concerns']
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your “{}” learning circle in {} has been created!'.format(lc.name, lc.city))
        self.assertIn('faci@example.net', mail.outbox[0].to)
        self.assertIn('thepeople@p2pu.org', mail.outbox[0].cc)
        self.assertIn('org@niz.er', mail.outbox[0].cc)
        self.assertEqual(len(mail.outbox[0].cc), 2)


    def test_update_learning_circle(self):
        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()
        c = Client()
        c.login(username='faci@example.net', password='password')
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
                { "meeting_date": "2018-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2018-02-19", "meeting_time": "17:01" },
            ],
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)

        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)

        # Update learning circle
        lc = StudyGroup.objects.all().last()
        self.assertFalse(lc.draft)
        url = '/api/learning-circle/{}/'.format(lc.pk)
        data['course'] = 1
        data["description"] = "Lets learn something else"
        data["name"] = "A new LC name"

        # date shouldn't matter, but lets make it after the lc started
        with freeze_time('2019-03-01'):
            resp = c.post(url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json()['status'], 'updated')

        lc = StudyGroup.objects.all().last()
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.course.id, 1)
        self.assertEqual(lc.description, "Lets learn something else")

        # test that reminders were regenerated
        self.assertIn('A new LC name', lc.reminder_set.first().email_subject)


    def test_update_learning_circle_date(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()
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
                { "meeting_date": "2018-12-15", "meeting_time": "17:01" },
                { "meeting_date": "2018-12-22", "meeting_time": "17:01" },
            ],
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.meeting_set.active().count(), 2)


        # update more than 2 days before start
        with freeze_time("2018-12-12"):
            data['meetings'] = [
                { "meeting_date": "2018-12-20", "meeting_time": "17:01" },
                { "meeting_date": "2018-12-27", "meeting_time": "17:01" },
            ]
            url = '/api/learning-circle/{}/'.format(lc.pk)
            resp = c.post(url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(resp.json(), {
                "status": "updated",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
            })

            lc = StudyGroup.objects.all().last()
            self.assertEqual(StudyGroup.objects.all().count(), 5)
            self.assertEqual(lc.start_date, datetime.date(2018, 12, 20))
            self.assertEqual(lc.meeting_set.active().count(), 2)


    def test_update_draft_learning_circle_date(self):
        c = Client()
        c.login(username='faci@example.net', password='password')
        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()
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
            "draft": True,
            "meetings": [
                { "meeting_date": "2018-12-15", "meeting_time": "17:01" },
                { "meeting_date": "2018-12-22", "meeting_time": "17:01" },
            ],
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        with freeze_time('2018-12-01'):
            resp = c.post(url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(resp.status_code, 200)

        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.meeting_set.active().count(), 2)

        # update less than 2 days before
        with freeze_time("2018-12-14"):
            data["meetings"] = [
                { "meeting_date": "2018-12-20", "meeting_time": "17:01" },
                { "meeting_date": "2018-12-27", "meeting_time": "17:01" },
            ]
            url = '/api/learning-circle/{}/'.format(lc.pk)
            resp = c.post(url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json(), {
                "status": "updated",
                "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
            })
            lc = StudyGroup.objects.all().last()
            self.assertEqual(StudyGroup.objects.all().count(), 5)
            self.assertEqual(lc.start_date, datetime.date(2018, 12, 20))
            self.assertEqual(lc.meeting_set.active().count(), 2)

        # update more than 2 days before
        with freeze_time("2018-12-12"):
            data["meetings"] = [
                { "meeting_date": "2018-12-19", "meeting_time": "17:01" },
                { "meeting_date": "2018-12-26", "meeting_time": "17:01" },
            ]
            url = '/api/learning-circle/{}/'.format(lc.pk)
            resp = c.post(url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(resp.json(), {
                "status": "updated",
                "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
            })
            lc = StudyGroup.objects.all().last()
            self.assertEqual(StudyGroup.objects.all().count(), 5)
            self.assertEqual(lc.start_date, datetime.date(2018, 12, 19))
            self.assertEqual(lc.meeting_set.active().count(), 2)


    @freeze_time('2018-01-20')
    def test_publish_learning_circle(self):
        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()
        c = Client()
        c.login(username='faci@example.net', password='password')
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
            "meetings": [
                { "meeting_date": "2018-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2018-02-19", "meeting_time": "17:01" },
            ],
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json(), {
            "status": "created",
            "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
        })
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.meeting_set.all().count(), 2)
        data['draft'] = False
        # Update learning circle
        url = '/api/learning-circle/{}/'.format(lc.pk)
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        lc = StudyGroup.objects.all().last()
        self.assertEqual(resp.json()['status'], 'updated')
        self.assertEqual(StudyGroup.objects.all().count(), 5)
        self.assertEqual(lc.meeting_set.all().count(), 2)


    def test_get_learning_circles(self):
        c = Client()
        resp = c.get('/api/learningcircles/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 4)


    def test_get_learning_circles_unicode(self):
        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()
        c = Client()
        c.login(username='faci@example.net', password='password')
        data = {
            "course": 3,
            "description": "Lets learn something",
            "course_description": "A real great course",
            "venue_name": "الصحة النفسية للطفل",
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
                { "meeting_date": "2018-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2018-02-19", "meeting_time": "17:01" },
            ],
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        with freeze_time('2018-01-20'):
            resp = c.post(url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(resp.status_code, 200)
            lc = StudyGroup.objects.all().last()
            self.assertEqual(resp.json(), {
                "status": "created",
                "studygroup_url": "{}://{}/en/studygroup/{}/".format(settings.PROTOCOL, settings.DOMAIN, lc.pk)
            })
            self.assertEqual(StudyGroup.objects.all().count(), 5)

        c = Client()
        resp = c.get('/api/learningcircles/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 5)


    def test_get_learning_circles_invalid_venue_name(self):
        self.facilitator.profile.email_confirmed_at = timezone.now()
        self.facilitator.profile.save()
        c = Client()
        c.login(username='faci@example.net', password='password')
        data = {
            "course": 3,
            "description": "Lets learn something",
            "course_description": "A real great course",
            "venue_name": "/@@",
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
                { "meeting_date": "2018-02-12", "meeting_time": "17:01" },
                { "meeting_date": "2018-02-19", "meeting_time": "17:01" },
            ],
        }
        url = '/api/learning-circle/'
        self.assertEqual(StudyGroup.objects.all().count(), 4)
        with freeze_time('2018-01-20'):
            resp = c.post(url, data=json.dumps(data), content_type='application/json')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json(), {
                "status": "error",
                "errors": {"venue_name": [
                    'Venue name should include at least one alpha-numeric character.'
                ]},
            })
            self.assertEqual(StudyGroup.objects.all().count(), 4)

    def test_get_learning_circles_drafts(self):
        c = Client()
        sg = StudyGroup.objects.get(pk=1)
        sg.draft = True
        sg.save()

        # exclude drafts by default
        resp = c.get('/api/learningcircles/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 3)

        # include drafts
        resp = c.get('/api/learningcircles/?draft=true')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 4)
        self.assertEqual(resp.json()["items"][0]['id'], 1)
        self.assertEqual(resp.json()["items"][0]['draft'], True)



    def test_get_learning_circles_by_weekday(self):
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2018,1,26)
        sg.save()
        sg = StudyGroup.objects.get(pk=2)
        sg.start_date = datetime.date(2018,1,27)
        sg.save()
        c = Client()
        # Friday and Saturday
        resp = c.get('/api/learningcircles/?weekdays=4,5')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 2)


    def test_get_learning_circles_full_text_search(self):
        c = Client()

        # partial word match

        resp = c.get('/api/learningcircles/', {'q': 'aca'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["items"][0]["course"]["title"], "Academic Writing")
        self.assertEqual(data["items"][1]["course"]["provider"], "Khan Academy")

        resp = c.get('/api/learningcircles/', {'q': 'acad'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["items"][0]["course"]["title"], "Academic Writing")
        self.assertEqual(data["items"][1]["course"]["provider"], "Khan Academy")

        resp = c.get('/api/learningcircles/', {'q': 'acade'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["items"][0]["course"]["title"], "Academic Writing")
        self.assertEqual(data["items"][1]["course"]["provider"], "Khan Academy")

        resp = c.get('/api/learningcircles/', {'q': 'academ'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["items"][0]["course"]["title"], "Academic Writing")
        self.assertEqual(data["items"][1]["course"]["provider"], "Khan Academy")

        resp = c.get('/api/learningcircles/', {'q': 'writ'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["items"][0]["course"]["title"], "Academic Writing")

        resp = c.get('/api/learningcircles/', {'q': 'writing'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["items"][0]["course"]["title"], "Academic Writing")


        # full word match

        resp = c.get('/api/learningcircles/', {'q': 'academy'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["items"][0]["course"]["provider"], "Khan Academy")

        resp = c.get('/api/learningcircles/', {'q': 'academic'})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["items"][0]["course"]["title"], "Academic Writing")


    @freeze_time("2019-05-31")
    def test_get_learning_circles_by_scope(self):
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2019,6,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        sg = StudyGroup.objects.get(pk=2)
        sg.start_date = datetime.date(2019,5,30)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        sg = StudyGroup.objects.get(pk=3)
        sg.start_date = datetime.date(2019,5,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        sg = StudyGroup.objects.get(pk=4)
        sg.start_date = datetime.date(2019,5,30)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.draft = True
        sg.save()

        c = Client()

        # active scope
        resp = c.get('/api/learningcircles/?scope=active&draft=true')
        data = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["items"][0]["id"], 1)
        self.assertEqual(data["items"][1]["id"], 2)
        self.assertEqual(data["items"][2]["id"], 4)
        self.assertEqual(data["items"][2]["draft"], True)

        # upcoming scope
        resp = c.get('/api/learningcircles/?scope=upcoming&draft=true')
        data = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data["count"], 2)
        self.assertEqual(data["items"][0]["id"], 1)
        self.assertEqual(data["items"][1]["id"], 4)

        # current scope
        resp = c.get('/api/learningcircles/?scope=current')
        data = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(data["items"][0]["id"], 2)

        # completed scope
        resp = c.get('/api/learningcircles/?scope=completed')
        data = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(data["items"][0]["id"], 3)


    @freeze_time("2019-05-31")
    def test_get_learning_circles_next_meeting(self):
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2019,5,30)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        c = Client()

        resp = c.get('/api/learningcircles/?scope=active')
        data = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(data["items"][0]["next_meeting_date"], "2019-06-06")


    @freeze_time("2015-03-21")
    def test_get_learning_circles_last_meeting(self):
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2015,2,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        c = Client()

        resp = c.get('/api/learningcircles/?scope=completed')
        data = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 1)
        self.assertEqual(data["items"][0]["last_meeting_date"], "2015-02-15")


    @freeze_time("2019-05-31")
    def test_get_learning_circles_signup_open(self):
        # open for signup
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2019,6,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # closed for signup because it's set as closed
        sg = StudyGroup.objects.get(pk=2)
        sg.start_date = datetime.date(2019,5,30)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = False
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # closed for signup because the last meeting is in the past
        sg = StudyGroup.objects.get(pk=3)
        sg.start_date = datetime.date(2019,5,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # doesn't show up in results because it's in draft
        sg = StudyGroup.objects.get(pk=4)
        sg.start_date = datetime.date(2019,5,30)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.draft = True
        sg.save()

        c = Client()

        # open for signup
        resp = c.get('/api/learningcircles/?signup=open')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["signup_open_count"], 1)
        self.assertEqual(result["signup_closed_count"], 2)
        self.assertEqual(result['items'][0]['signup_open'], True)

        # closed for signup
        resp = c.get('/api/learningcircles/?signup=closed')
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["signup_open_count"], 1)
        self.assertEqual(result["signup_closed_count"], 2)
        self.assertEqual(result['items'][0]['signup_open'], False)
        self.assertEqual(result['items'][1]['signup_open'], False)


    @freeze_time("2019-05-31")
    def test_get_learning_cirlces_order(self):
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2019,5,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        sg = StudyGroup.objects.get(pk=2)
        sg.start_date = datetime.date(2019,5,8)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        sg = StudyGroup.objects.get(pk=3)
        sg.start_date = datetime.date(2019,5,15)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        sg = StudyGroup.objects.get(pk=4)
        sg.start_date = datetime.date(2019,5,30)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()

        c = Client()

        # ordered by first meeting date (asc)
        resp = c.get('/api/learningcircles/?order=first_meeting_date')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 4)
        self.assertEqual(result['items'][0]['id'], 1)
        self.assertEqual(result['items'][1]['id'], 2)

        # ordered by last meeting date (desc)
        resp = c.get('/api/learningcircles/?order=last_meeting_date')
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 4)
        self.assertEqual(result['items'][0]['id'], 4)
        self.assertEqual(result['items'][1]['id'], 3)


    def test_get_learning_circles_by_topics(self):
        c = Client()

        # single topic
        resp = c.get('/api/learningcircles/?topics=math')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]['course']['id'], 1)

        # multiple topics
        resp = c.get('/api/learningcircles/?topics=math,writing')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["items"][0]['course']['id'], 2)
        self.assertEqual(result["items"][1]['course']['id'], 1)


    def test_get_learning_circles_by_location(self):
        sg = StudyGroup.objects.get(pk=1)
        # boston coordinates
        sg.latitude = '42.360200'
        sg.longitude = '-71.058300'
        sg.save()

        c = Client()

        resp = c.get('/api/learningcircles/?latitude=42.372028&longitude=-71.103081&distance=50') # cambridge coords
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]['id'], 1)

        resp = c.get('/api/learningcircles/?latitude=43.466120&longitude=-80.525158&distance=50') # waterloo coords
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 0)



    def test_get_learning_circles_limit_offset(self):
        c = Client()
        resp = c.get('/api/learningcircles/?limit=1&offset=0')
        result = resp.json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["limit"], 1)
        self.assertEqual(result["offset"], 0)
        self.assertEqual(len(result["items"]), 1)

        resp = c.get('/api/learningcircles/?limit=1&offset=1')
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["limit"], 1)
        self.assertEqual(result["offset"], 1)
        self.assertEqual(len(result["items"]), 1)


    def test_get_learning_circles_by_city(self):
        sg = StudyGroup.objects.get(pk=4)
        sg.city = 'Kitchener'
        sg.save()

        c = Client()
        resp = c.get('/api/learningcircles/?city=Kitchener')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]['id'], 4)


    def test_get_learning_circles_by_team(self):

        sg_count = StudyGroup.objects.count()
        facilitator2 = User.objects.get(pk=2)
        self.assertEqual(facilitator2.teammembership_set.active().count(), 1)
        team = facilitator2.teammembership_set.active().first().team
        sgdata = dict(            
            course=Course.objects.first(),
            facilitator=facilitator2,
            description='blah',
            venue_name='ACME public library',
            venue_address='ACME rd 1',
            venue_details='venue_details',
            city='city',
            latitude=0,
            longitude=0,
            start_date=datetime.date(2010,1,1),
            end_date=datetime.date(2010,1,1) + datetime.timedelta(weeks=6),
            meeting_time=datetime.time(12,0),
            duration=90,
            timezone='GMT',
            facilitator_goal='the_facilitator_goal',
            facilitator_concerns='the_facilitators_concerns',
            draft=False,
        )
        sg = StudyGroup(**sgdata)
        sg.save()

        sg_ids = [sg.pk]

        self.assertEqual(sg.team_id, team.id)

        meeting_dates = generate_all_meeting_dates(
            sg.start_date, sg.meeting_time, 6
        )
        generate_meetings_from_dates(sg, meeting_dates)

        sgdata['name'] = 'another lc'
        sg = StudyGroup(**sgdata)
        sg.save()
        sg_ids += [sg.id]
        meeting_dates = generate_all_meeting_dates(
            sg.start_date, sg.meeting_time, 6
        )
        generate_meetings_from_dates(sg, meeting_dates)

        self.assertEqual(sg.team_id, team.id)
        self.assertEqual(sg_count + 2, StudyGroup.objects.count())

        self.assertEqual(StudyGroup.objects.active().filter(team=team).count(), 2)

        c = Client()
        resp = c.get(f'/api/learningcircles/?team_id={team.id}')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 2)
        self.assertIn(result["items"][0]['id'], sg_ids)
        self.assertIn(result["items"][1]['id'], sg_ids)

        # remove user from team
        facilitator2.teammembership_set.active().first().delete()
        
        # ensure learning circles are still returned for the team
        resp = c.get(f'/api/learningcircles/?team_id={team.id}')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 2)
        self.assertIn(result["items"][0]['id'], sg_ids)
        self.assertIn(result["items"][1]['id'], sg_ids)


    def test_get_learning_circle_by_id(self):
        c = Client()
        resp = c.get('/api/learningcircles/?id=3')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]['id'], 3)


    def test_get_learning_circles_by_user(self):
        factory = RequestFactory()
        request = factory.get('/api/learningcircles/?user=true')
        user = self.facilitator
        sg = StudyGroup.objects.get(pk=2)
        sg.created_by = user
        sg.save()

        request.user = user

        resp = LearningCircleListView.as_view()(request)
        result = json.loads(resp.content)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]['id'], 2)

    def test_get_learning_circle_cities(self):
        c = Client()
        resp = c.get('/api/learningcircles/cities/')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["items"][0], { 'label': 'Boston', 'value': 'Boston' })
        self.assertEqual(result["items"][1], { 'label': 'Chicago', 'value': 'Chicago' })
        self.assertEqual(result["items"][2], { 'label': 'Kansas City', 'value': 'Kansas City' })
        self.assertEqual(result["items"][3], { 'label': 'Toronto', 'value': 'Toronto' })


    @freeze_time("2019-05-31")
    def test_get_learning_circles_no_meetings(self):
        # end_date in the past
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2019,5,14)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # start_date in past, end_date in the future
        sg = StudyGroup.objects.get(pk=2)
        sg.start_date = datetime.date(2019,5,30)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # start_date in future
        sg = StudyGroup.objects.get(pk=3)
        sg.start_date = datetime.date(2019,6,2)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        c = Client()
        resp = c.get('/api/learningcircles/?signup=open')
        result = resp.json()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 2)

        self.assertEqual(result["items"][0]["id"], 2)
        self.assertEqual(result["items"][0]["last_meeting_date"], '2019-06-13')
        self.assertEqual(result["items"][1]["id"], 3)
        self.assertEqual(result["items"][1]["last_meeting_date"], '2019-06-16')


    @freeze_time("2019-05-31")
    def test_get_learning_circles_status(self):
        # upcoming
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2019,6,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # in progress
        sg = StudyGroup.objects.get(pk=2)
        sg.start_date = datetime.date(2019,5,30)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # closed
        sg = StudyGroup.objects.get(pk=3)
        sg.start_date = datetime.date(2019,5,30)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = False
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # completed
        sg = StudyGroup.objects.get(pk=4)
        sg.start_date = datetime.date(2019,5,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()

        c = Client()

        resp = c.get('/api/learningcircles/')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["signup_open_count"], 2)
        self.assertEqual(result["signup_closed_count"], 2)
        self.assertEqual(result['items'][0]['status'], 'upcoming')
        self.assertEqual(result['items'][1]['status'], 'in_progress')
        self.assertEqual(result['items'][2]['status'], 'closed')
        self.assertEqual(result['items'][3]['status'], 'completed')


    @freeze_time("2019-05-31")
    def test_get_learning_circles_status_closed_completed(self):
        # closed upcoming
        sg = StudyGroup.objects.get(pk=1)
        sg.start_date = datetime.date(2019,6,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = False
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # closed in progress
        sg = StudyGroup.objects.get(pk=2)
        sg.start_date = datetime.date(2019,5,30)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = False
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # closed in past (should be completed status)
        sg = StudyGroup.objects.get(pk=3)
        sg.start_date = datetime.date(2019,4,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = False
        sg.save()
        sg.refresh_from_db()
        generate_all_meetings(sg)

        # open in past (should be completed status)
        sg = StudyGroup.objects.get(pk=4)
        sg.start_date = datetime.date(2019,4,1)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=2)
        sg.signup_open = True
        sg.save()

        c = Client()

        resp = c.get('/api/learningcircles/')
        result = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(result["count"], 4)
        self.assertEqual(result["signup_open_count"], 0)
        self.assertEqual(result["signup_closed_count"], 4)
        self.assertEqual(result['items'][0]['status'], 'closed')
        self.assertEqual(result['items'][1]['status'], 'closed')
        self.assertEqual(result['items'][2]['status'], 'completed')
        self.assertEqual(result['items'][3]['status'], 'completed')


