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

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import Rsvp
from studygroups.models import Reminder
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import Feedback
from studygroups.models import generate_all_meetings
from studygroups.utils import gen_rsvp_querystring
from studygroups.tasks import send_reminders
from studygroups.tasks import send_reminder
from custom_registration.models import create_user
from custom_registration.models import confirm_user_email

import datetime
import urllib.request, urllib.parse, urllib.error
import json



"""
Tests for when facilitators interact with the system
"""
class TestFacilitatorViews(TestCase):

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


    def test_user_forbidden(self):
        user = create_user('bob@example.net', 'bob', 'test', 'password')
        c = Client()
        c.login(username='bob@example.net', password='password')
        def assertForbidden(url):
            resp = c.get(url)
            self.assertEqual(resp.status_code, 403)
        assertForbidden('/en/organize/')
        assertForbidden('/en/report/weekly/')
        assertForbidden('/en/studygroup/1/')
        assertForbidden('/en/studygroup/1/edit/')
        assertForbidden('/en/studygroup/1/message/compose/')
        assertForbidden('/en/studygroup/1/message/edit/1/')
        assertForbidden('/en/studygroup/1/message/1/')
        assertForbidden('/en/studygroup/1/member/add/')
        assertForbidden('/en/studygroup/1/member/1/delete/')
        assertForbidden('/en/studygroup/1/meeting/create/')
        assertForbidden('/en/studygroup/1/meeting/2/edit/')
        assertForbidden('/en/studygroup/1/meeting/2/delete/')


    def test_facilitator_access(self):
        user = create_user('bob@example.net', 'bob', 'test', 'password')
        sg = StudyGroup.objects.get(pk=1)
        sg.facilitator = user
        sg.save()
        c = Client()
        c.login(username='bob@example.net', password='password')
        def assertAllowed(url):
            resp = c.get(url)
            #TODO not sure if it's a good idea to include 404 here!
            self.assertIn(resp.status_code, [200, 301, 302])

        def assertStatus(url, status):
            resp = c.get(url)
            self.assertEqual(resp.status_code, status)
        assertAllowed('/en/studygroup/1/')
        assertAllowed('/en/studygroup/1/edit/')
        assertAllowed('/en/studygroup/1/message/compose/')
        assertStatus('/en/studygroup/1/message/edit/1111/', 404)
        assertAllowed('/en/studygroup/1/member/add/')
        assertStatus('/en/studygroup/1/member/2111/delete/', 404)
        assertAllowed('/en/studygroup/1/meeting/create/')
        assertStatus('/en/studygroup/1/meeting/2111/edit/', 404)
        assertStatus('/en/studygroup/1/meeting/2111/delete/', 404)


    def test_create_study_group(self):
        user = create_user('bob@example.net', 'bob', 'test', 'password')
        mail.outbox = []
        c = Client()
        c.login(username='bob@example.net', password='password')
        data = self.STUDY_GROUP_DATA.copy()
        data['start_date'] = '07/25/2018',
        data['meeting_time'] = '07:00 PM',
        with freeze_time('2018-07-20'):
            resp = c.post('/en/studygroup/create/legacy/', data)
            sg = StudyGroup.objects.last()
            self.assertRedirects(resp, '/en/studygroup/{}/'.format(sg.pk))
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEquals(study_groups.count(), 1)
        lc = study_groups.first()
        self.assertEquals(study_groups.first().meeting_set.count(), 6)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your “{}” learning circle in {} has been created!'.format(lc.name, lc.city))
        self.assertIn('bob@example.net', mail.outbox[0].to)
        self.assertIn('thepeople@p2pu.org', mail.outbox[0].cc)
        self.assertIn('community@localhost', mail.outbox[0].cc)


    @patch('custom_registration.signals.handle_new_facilitator')
    def test_publish_study_group(self, handle_new_facilitator):
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        confirm_user_email(user)
        c = Client()
        c.login(username='bob@example.net', password='password')

        with freeze_time('2018-07-20'):
            resp = c.post('/api/learning-circle/', data=json.dumps(self.STUDY_GROUP_DATA), content_type='application/json')
            self.assertEqual(resp.json()['status'], 'created')
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEqual(study_groups.count(), 1)
        lc = study_groups.first()
        self.assertEqual(lc.meeting_set.count(), 6)
        resp = c.post('/en/studygroup/{0}/publish/'.format(lc.pk))
        self.assertRedirects(resp, '/en/studygroup/{0}/'.format(lc.pk))
        study_group = StudyGroup.objects.get(pk=lc.pk)
        self.assertEqual(study_group.draft, False)
        self.assertEqual(study_group.meeting_set.count(), 6)


    @patch('custom_registration.signals.handle_new_facilitator')
    def test_publish_study_group_email_unconfirmed(self, handle_new_facilitator):
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        c = Client()
        c.login(username='bob@example.net', password='password')

        with freeze_time('2018-07-20'):
            resp = c.post('/api/learning-circle/', data=json.dumps(self.STUDY_GROUP_DATA), content_type='application/json')
            self.assertEqual(resp.json()['status'], 'created')
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEqual(study_groups.count(), 1)
        lc = study_groups.first()
        resp = c.post('/en/studygroup/{0}/publish/'.format(lc.pk))
        self.assertRedirects(resp, '/en/studygroup/{}/'.format(lc.pk))
        study_group = StudyGroup.objects.get(pk=lc.pk)
        self.assertEqual(study_group.draft, True)


    @patch('custom_registration.signals.handle_new_facilitator')
    def test_draft_study_group_actions_disabled(self, handle_new_facilitator):
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        confirm_user_email(user)
        c = Client()
        c.login(username='bob@example.net', password='password')

        with freeze_time('2018-07-20'):
            resp = c.post('/api/learning-circle/', data=json.dumps(self.STUDY_GROUP_DATA), content_type='application/json')
            self.assertEqual(resp.json()['status'], 'created')
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEqual(study_groups.count(), 1)
        self.assertEqual(study_groups.first().meeting_set.count(), 6)

        # can add a meeting
        self.assertEqual(study_groups.first().pk, StudyGroup.objects.last().pk)
        url_base = '/en/studygroup/{0}'.format(study_groups.first().pk)
        resp = c.get(url_base + '/meeting/create/')
        self.assertEqual(resp.status_code, 200)
        meeting_data = {
            "meeting_date": "2018-03-17",
            "meeting_time": "04:00 PM",
            "study_group": study_groups.first().pk,
        }
        resp = c.post(url_base + '/meeting/create/', data=meeting_data)
        self.assertRedirects(resp, url_base + '/')
        self.assertEqual(StudyGroup.objects.last().meeting_set.count(), 7)

        expected_redirect_url = '/en/studygroup/{0}/'.format(study_groups.first().pk)

        # cannot send a message
        resp = c.get('/en/studygroup/{0}/message/compose/'.format(study_groups.first().pk))
        self.assertRedirects(resp, expected_redirect_url)
        mail_data = {
            u'study_group': study_groups.first().pk,
            u'email_subject': 'does not matter',
            u'email_body': 'does not matter',
        }
        mail.outbox = []
        resp = c.post(url_base + '/message/compose/', mail_data)
        self.assertRedirects(resp, expected_redirect_url)
        self.assertEqual(len(mail.outbox), 0)

        # cannot add a learner
        resp = c.get('/en/studygroup/{0}/member/add/'.format(study_groups.first().pk))
        self.assertRedirects(resp, expected_redirect_url)
        learner_data = {
            "email": "learn@example.net",
            "name": "no name",
            "study_group": "515",
        }
        resp = c.post(url_base + '/member/add/', data=learner_data)
        self.assertRedirects(resp, expected_redirect_url)
        self.assertEqual(StudyGroup.objects.last().application_set.count(), 0)


    def test_update_study_group_legacy_view(self):
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        confirm_user_email(user)
        c = Client()
        c.login(username='bob@example.net', password='password')
        data = self.STUDY_GROUP_DATA.copy()
        data['start_date'] = '12/25/2018'
        data['meeting_time'] = '07:00 PM'
        with freeze_time("2018-12-20"):
            resp = c.post('/en/studygroup/create/legacy/', data)
            sg = StudyGroup.objects.last()
            self.assertRedirects(resp, '/en/studygroup/{}/'.format(sg.pk))
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEquals(study_groups.count(), 1)
        lc = study_groups.first()
        self.assertEquals(study_groups.first().meeting_set.active().count(), 6)

        # updates allowed for drafts
        with freeze_time("2018-12-28"):
            data['start_date'] = '12/25/2018'
            data['meeting_time'] = '07:10 PM'
            edit_url = '/en/studygroup/{}/edit/legacy/'.format(lc.pk)
            resp = c.post(edit_url, data)
            self.assertRedirects(resp, '/en/studygroup/{}/'.format(lc.pk))
            study_group = StudyGroup.objects.get(pk=study_groups.first().pk)
            self.assertEqual(study_group.start_date, datetime.date(2018, 12, 25))
            self.assertEqual(study_group.meeting_time, datetime.time(19, 10))
            self.assertEqual(study_group.meeting_set.active().count(), 6)

        resp = c.post('/en/studygroup/{0}/publish/'.format(lc.pk))
        self.assertRedirects(resp, '/en/studygroup/{}/'.format(lc.pk))
        study_group = StudyGroup.objects.get(pk=study_groups.first().pk)
        self.assertEqual(study_group.draft, False)
        self.assertEqual(study_group.meeting_set.active().count(), 6)

        # update not allowed
        with freeze_time("2018-12-24"):
            data['start_date'] = '12/24/2018'
            data['meeting_time'] = '07:00 PM'
            data['weeks'] = 4
            edit_url = '/en/studygroup/{}/edit/legacy/'.format(study_group.pk)
            resp = c.post(edit_url, data)
            self.assertEqual(resp.status_code, 200)
            study_group = StudyGroup.objects.get(pk=study_groups.first().pk)
            self.assertEqual(study_group.start_date, datetime.date(2018, 12, 25))
            self.assertEqual(study_group.meeting_set.active().count(), 6)

        # update allowed
        with freeze_time("2018-12-22"):
            data['start_date'] = '12/24/2018'
            data['meeting_time'] = '07:00 PM'
            data['weeks'] = 3
            edit_url = '/en/studygroup/{}/edit/legacy/'.format(study_group.pk)
            resp = c.post(edit_url, data)
            self.assertRedirects(resp, '/en/studygroup/{}/'.format(study_group.pk))
            study_group = StudyGroup.objects.get(pk=study_groups.first().pk)
            self.assertEqual(study_group.start_date, datetime.date(2018, 12, 24))
            self.assertEqual(study_group.meeting_set.active().count(), 3)

        meeting_times = [(meeting.meeting_date, meeting.meeting_time) for meeting in study_group.meeting_set.active().all()]
        self.assertEqual(meeting_times, [
            (datetime.date(2018,12,24), datetime.time(19,0)),
            (datetime.date(2018,12,31), datetime.time(19,0)),
            (datetime.date(2019,1,7), datetime.time(19,0)),
        ])

        # missing weeks
        with freeze_time("2018-12-20"):
            del data['weeks']
            resp = c.post('/en/studygroup/create/legacy/', data)
            self.assertEqual(resp.status_code, 200)
            expected_error_message = 'Please provide the length of the learning circle in weeks'
            self.assertFormError(resp, 'form', 'weeks', expected_error_message)



    @patch('custom_registration.signals.handle_new_facilitator')
    def test_study_group_unicode_venue_name(self, handle_new_facilitator):
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        confirm_user_email(user)
        c = Client()
        c.login(username='bob@example.net', password='password')
        sgd = self.STUDY_GROUP_DATA.copy()
        sgd['draft'] = False
        sgd['venue_name'] = 'Быстрее и лучше'
        sgd['start_date'] = (datetime.datetime.now() + datetime.timedelta(weeks=2)).date().isoformat()
        resp = c.post('/api/learning-circle/', data=json.dumps(sgd), content_type='application/json')
        self.assertEqual(resp.json()['status'], 'created')
        study_groups = StudyGroup.objects.filter(facilitator=user)
        study_group = study_groups.first()
        self.assertEqual(study_groups.count(), 1)
        self.assertEqual(study_group.meeting_set.count(), 6)

        resp = c.get('/en/studygroup/{}/'.format(study_group.id))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('/en/signup/%D0%B1%D1%8B%D1%81%D1%82%D1%80%D0%B5%D0%B5-%D0%B8-%D0%BB%D1%83%D1%87%D1%88%D0%B5-', resp.content.decode("utf-8"))


    @patch('custom_registration.signals.handle_new_facilitator')
    def test_create_study_group_venue_name_validation(self, handle_new_facilitator):
        user = create_user('bob@example.net', 'bob123', 'test', 'password', False)
        c = Client()
        c.login(username='bob@example.net', password='password')
        data = self.STUDY_GROUP_DATA.copy()
        data['start_date'] = '07/25/2019',
        data['meeting_time'] = '07:00 PM',
        data['venue_name'] = '#@$@'
        with freeze_time('2019-07-20'):
            resp = c.post('/en/studygroup/create/legacy/', data)
            self.assertEquals(resp.status_code, 200)
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEquals(study_groups.count(), 0)


    @patch('studygroups.models.learningcircle.current_app')
    def test_edit_meeting(self, current_app):
        # Create studygroup
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        confirm_user_email(user)
        c = Client()
        c.login(username='bob@example.net', password='password')
        with freeze_time('2018-07-20'):
            resp = c.post('/api/learning-circle/', data=json.dumps(self.STUDY_GROUP_DATA), content_type='application/json')
            self.assertEqual(resp.json()['status'], 'created')
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEqual(study_groups.count(), 1)
        lc = study_groups.first()
        self.assertEqual(lc.meeting_set.count(), 6)
        resp = c.post('/en/studygroup/{0}/publish/'.format(lc.pk))
        self.assertRedirects(resp, '/en/studygroup/{0}/'.format(lc.pk))
        study_group = StudyGroup.objects.get(pk=lc.pk)
        self.assertEqual(study_group.draft, False)
        self.assertEqual(study_group.meeting_set.count(), 6)
        self.assertEqual(study_group.reminder_set.count(), 6)

        # update 1st meeting with unsent reminder
        meeting = study_group.meeting_set.order_by('meeting_date').first()
        meeting_id = meeting.pk
        old_reminder_body = meeting.reminder_set.first().email_body
        update = {
            "meeting_date": "2018-07-26",
            "meeting_time": "07:00 PM",
            "study_group": study_group.pk,
        }
        with freeze_time('2018-07-20'):
            resp = c.post('/en/studygroup/{0}/meeting/{1}/edit/'.format(study_group.pk, meeting.pk), update)
        self.assertRedirects(resp, '/en/studygroup/{}/'.format(study_group.pk))
        meeting.refresh_from_db()
        self.assertEqual(meeting.meeting_date, datetime.date(2018, 7, 26))
        current_app.send_task.assert_not_called()  # no meeting change notification sent
        self.assertNotEqual(meeting.reminder_set.first().email_body, old_reminder_body)  # reminder regenerated
        self.assertEqual(study_group.reminder_set.count(), 6)

        # send it
        with freeze_time('2018-07-25'):
            self.assertEqual(Reminder.objects.filter(study_group=study_group, sent_at__isnull=False).count(), 0)
            send_reminders()
            self.assertEqual(Reminder.objects.filter(study_group=study_group, sent_at__isnull=False).count(), 1)

        # and then update it afterwards to be in the future again
        with freeze_time('2018-07-27'):
            meeting.refresh_from_db()
            self.assertTrue(meeting.meeting_datetime() < timezone.now())
            self.assertEquals(Reminder.objects.count(), 6)
            update['meeting_date'] = '2018-07-30'
            resp = c.post('/en/studygroup/{0}/meeting/{1}/edit/'.format(study_group.pk, meeting.pk), update)
            self.assertRedirects(resp, '/en/studygroup/{}/'.format(study_group.pk))
            meeting.refresh_from_db()
            self.assertFalse(current_app.send_task.called)  # meeting change notification should not be sent
            self.assertEquals(Reminder.objects.count(), 7)  # old reminder is kept


        # update it before the meeting to be further in the future
        with freeze_time('2018-07-29'):
            meeting.refresh_from_db()
            self.assertTrue(meeting.meeting_datetime() > timezone.now())
            send_reminders()
            update['meeting_date'] = '2019-08-02'
            resp = c.post('/en/studygroup/{0}/meeting/{1}/edit/'.format(study_group.pk, meeting.pk), update)
            self.assertRedirects(resp, '/en/studygroup/{}/'.format(study_group.pk))
            meeting.refresh_from_db()
            current_app.send_task.assert_called_once()  # meeting change notification should be sent
            self.assertEquals(meeting.reminder_set.count(), 1)
            self.assertEquals(Reminder.objects.count(), 8)  # old reminder should be kept


    @freeze_time('2021-02-25')
    def test_edit_reminder(self):
        c = Client()
        c.login(username='admin@test.com', password='password')
        signup_data = self.APPLICATION_DATA.copy()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        mail.outbox = []
        study_group = StudyGroup.objects.get(pk=1)
        study_group.start_date = datetime.date(2021, 3, 1)
        study_group.end_date = study_group.start_date + datetime.timedelta(weeks=5)
        study_group.save()

        signup_data = self.APPLICATION_DATA.copy()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)

        generate_all_meetings(study_group)
        self.assertEqual(study_group.meeting_set.active().count(), 6)
        self.assertEqual(study_group.reminder_set.count(), 6)
        meeting = study_group.meeting_set.active().first()
        reminder = meeting.reminder_set.first()

        url = '/en/studygroup/{0}/message/edit/{1}/'.format(signup_data['study_group'], reminder.id)

        email_body = '<p>hi, here is a link <a href="https://www.p2pu.org">p2pu</a></p><script>alert("MUHAHAHA")</script>'
        mail_data = {
            'study_group': study_group.id,
            'email_subject': 'GED® Prep Math study group meeting Thursday 7 May 6:00 PM at Edgewater',
            'email_body': email_body,
            'sms_body': 'The first study group for GED® Prep Math will meet next Thursday, May 7th, from 6:00 pm-7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!'
        }
        resp = c.post(url, mail_data)
        self.assertRedirects(resp, '/en/studygroup/1/')
        reminder.refresh_from_db()
        self.assertIn('&lt;script&gt;alert("MUHAHAHA")&lt;/script&gt;', reminder.email_body)
        self.assertIn('<a href="https://www.p2pu.org">p2pu</a>', reminder.email_body)

        mail.outbox = []
        send_reminder(reminder)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to[0], signup_data['email'])
        self.assertEqual(mail.outbox[1].to[0], 'facilitator@example.net')
        self.assertIn('/optout/confirm/?user=', mail.outbox[0].alternatives[0][0])
        self.assertIn('&lt;script&gt;alert("MUHAHAHA")&lt;/script&gt;', mail.outbox[0].alternatives[0][0])
        self.assertIn('<a href="https://www.p2pu.org">p2pu</a>', mail.outbox[0].alternatives[0][0])


    @patch('studygroups.tasks.send_message')
    def test_send_email(self, send_message):
        # Test sending a message
        c = Client()
        c.login(username='admin@test.com', password='password')
        signup_data = self.APPLICATION_DATA.copy()
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        mail.outbox = []

        url = '/en/studygroup/{0}/message/compose/'.format(signup_data['study_group'])
        email_body = 'Hi there!\n\nThe first study group for GED® Prep Math will meet this Thursday, May 7th, from 6:00 pm - 7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!\nFor any questions you can contact Emily at emily@p2pu.org.\n\nSee you soon'
        mail_data = {
            'study_group': signup_data['study_group'],
            'email_subject': 'GED® Prep Math study group meeting Thursday 7 May 6:00 PM at Edgewater',
            'email_body': email_body,
            'sms_body': 'The first study group for GED® Prep Math will meet next Thursday, May 7th, from 6:00 pm-7:45 pm at Edgewater on the 2nd floor. Feel free to bring a study buddy!'
        }
        resp = c.post(url, mail_data)
        self.assertRedirects(resp, '/en/studygroup/1/')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, mail_data['email_subject'])
        self.assertEqual(mail.outbox[0].from_email, 'P2PU <{}>'.format(settings.DEFAULT_FROM_EMAIL))
        self.assertFalse(send_message.called)
        self.assertIn('{}/en/optout/'.format(settings.DOMAIN), mail.outbox[0].body)


    @patch('studygroups.tasks.send_message')
    def test_send_sms(self, send_message):
        c = Client()
        c.login(username='admin@test.com', password='password')
        signup_data = self.APPLICATION_DATA.copy()
        signup_data['mobile'] = '+12812345678'
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        mail.outbox = []

        url = '/en/studygroup/{0}/message/compose/'.format(signup_data['study_group'])
        mail_data = {
            'study_group': signup_data['study_group'],
            'email_subject': 'test',
            'email_body': 'Email body',
            'sms_body': 'Sms body'
        }
        resp = c.post(url, mail_data)
        self.assertRedirects(resp, '/en/studygroup/1/')
        self.assertEqual(len(mail.outbox), 1)  # Send both email and text message
        self.assertTrue(send_message.called)


    @patch('studygroups.tasks.send_message')
    def test_dont_send_blank_sms(self, send_message):
        c = Client()
        c.login(username='admin@test.com', password='password')
        signup_data = self.APPLICATION_DATA.copy()
        signup_data['mobile'] = '+12812345678'
        resp = c.post('/en/signup/foo-bob-1/', signup_data)
        self.assertRedirects(resp, '/en/signup/1/success/')
        self.assertEqual(Application.objects.active().count(), 1)
        mail.outbox = []

        url = '/en/studygroup/{0}/message/compose/'.format(signup_data['study_group'])
        mail_data = {
            'study_group': signup_data['study_group'],
            'email_subject': 'test',
            'email_body': 'Email body'
        }
        resp = c.post(url, mail_data)
        self.assertRedirects(resp, '/en/studygroup/1/')
        self.assertEqual(len(mail.outbox), 1)  # Still send email
        self.assertFalse(send_message.called) # dont send sms


    def test_user_accept_invitation(self):
        organizer = create_user('organ@team.com', 'organ', 'test', '1234', False)
        faci1 = create_user('faci1@team.com', 'faci1', 'test', '1234', False)
        StudyGroup.objects.filter(pk=1).update(facilitator=faci1)

        # create team
        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)

        c = Client()
        c.login(username='faci1@team.com', password='1234')
        resp = c.get('/en/facilitator/team-invitation/')
        self.assertRedirects(resp, '/en/')

        invitation = TeamInvitation.objects.create(team=team, organizer=organizer, role=TeamMembership.MEMBER, email=faci1.email)
        self.assertTrue(TeamInvitation.objects.get(team=team, role=TeamMembership.MEMBER, email__iexact=faci1.email).responded_at is None)
        invitation_confirmation_url = reverse('studygroups_facilitator_invitation_confirm', args=(invitation.id,))
        resp = c.post(invitation_confirmation_url, {'response': 'yes'})
        self.assertRedirects(resp, '/en/')
        self.assertEqual(TeamMembership.objects.active().filter(team=team, role=TeamMembership.MEMBER, user=faci1).count(), 1)
        self.assertFalse(TeamInvitation.objects.get(team=team, role=TeamMembership.MEMBER, email__iexact=faci1.email).responded_at is None)


    def test_user_reject_invitation(self):
        organizer = create_user('organ@team.com', 'organ', 'test', '1234', False)
        faci1 = create_user('faci1@team.com', 'faci1', 'test', '1234', False)
        StudyGroup.objects.filter(pk=1).update(facilitator=faci1)

        # create team
        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)

        c = Client()
        c.login(username='faci1@team.com', password='1234')

        invitation = TeamInvitation.objects.create(team=team, organizer=organizer, role=TeamMembership.MEMBER, email=faci1.email)
        self.assertTrue(TeamInvitation.objects.get(team=team, role=TeamMembership.MEMBER, email__iexact=faci1.email).responded_at is None)
        invitation_confirmation_url = reverse('studygroups_facilitator_invitation_confirm', args=(invitation.id,))
        resp = c.post(invitation_confirmation_url, {'response': 'no'})
        self.assertRedirects(resp, '/en/')
        self.assertEqual(TeamMembership.objects.active().filter(team=team, role=TeamMembership.MEMBER, user=faci1).count(), 0)
        self.assertFalse(TeamInvitation.objects.get(team=team, role=TeamMembership.MEMBER, email__iexact=faci1.email).responded_at is None)


    def test_edit_course(self):
        user = create_user('bob@example.net', 'bob', 'test', 'password')
        course_data = dict(
            title='Course 1011',
            provider='CourseMagick',
            link='https://course.magick/test',
            caption='learn by means of magic',
            on_demand=True,
            topics='html,test',
            language='en',
            created_by=user
        )
        course = Course.objects.create(**course_data)
        c = Client()
        c.login(username='bob@example.net', password='password')
        # make sure bob123 can edit the course
        course_url = '/en/course/{}/edit/'.format(course.id)
        resp = c.get(course_url)
        course_data['topics'] = 'magic'
        resp = c.post(course_url, course_data)
        self.assertRedirects(resp, '/en/')
        self.assertEqual(Course.objects.get(pk=course.id).topics, 'magic')


    def test_cant_edit_other_facilitators_course(self):
        create_user('bob2@example.net', 'bob2', '2', 'password')
        user = create_user('bob@example.net', 'bob123', '123', 'password')
        course_data = dict(
            title='Course 1011',
            provider='CourseMagick',
            link='https://course.magick/test',
            caption='learn by means of magic',
            on_demand=True,
            topics='html,test',
            language='en',
            created_by=user
        )
        course = Course.objects.create(**course_data)
        c = Client()
        c.login(username='bob2@example.net', password='password')
        course_url = '/en/course/{}/edit/'.format(course.id)
        resp = c.get(course_url)
        self.assertEqual(resp.status_code, 403)
        course_data['topics'] = 'magic'
        resp = c.post(course_url, course_data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Course.objects.get(pk=course.id).topics, 'html,test')


    def test_cant_edit_used_course(self):
        user = create_user('bob@example.net', 'first', 'last', 'password')
        user2 = create_user('bob2@example.net', 'first', 'last', 'password')
        course_data = dict(
            title='Course 1011',
            provider='CourseMagick',
            link='https://course.magick/test',
            caption='learn by means of magic',
            on_demand=True,
            topics='html,test',
            language='en',
            created_by=user
        )
        course = Course.objects.create(**course_data)
        sg = StudyGroup.objects.get(pk=1)
        sg.course = course
        sg.facilitator = user2
        sg.save()
        c = Client()
        c.login(username='bob@example.net', password='password')
        # make sure bob123 can edit the course
        course_url = '/en/course/{}/edit/'.format(course.id)
        resp = c.get(course_url)
        self.assertRedirects(resp, '/en/')
        course_data['topics'] = 'magic'
        resp = c.post(course_url, course_data)
        self.assertRedirects(resp, '/en/')
        self.assertEqual(Course.objects.get(pk=course.id).topics, 'html,test')


    def test_study_group_facilitator_survey(self):
        facilitator = create_user('hi@example.net', 'bowie', 'wowie', 'password')
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
        c = Client()
        c.login(username='hi@example.net', password='password')
        feedback_url = '/en/studygroup/{}/facilitator_survey/?goal_rating=5'.format(sg.uuid)
        with self.settings(TYPEFORM_FACILITATOR_SURVEY_FORM='SOMESURVEYYOUGOTTHERE'):
            response = c.get(feedback_url)

        sg.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context_data['study_group_uuid']), str(sg.uuid))
        self.assertEqual(response.context_data['study_group'], sg)
        self.assertEqual(response.context_data['survey_id'], 'SOMESURVEYYOUGOTTHERE')
        self.assertEqual(response.context_data['course'], course.title)
        self.assertEqual(response.context_data['goal'], sg.facilitator_goal)
        self.assertEqual(response.context_data['goal_rating'], sg.facilitator_goal_rating)
        # TODO query string shouldn't update rating since that happens in code executed on the client
        # TODO consider add a frontend test for that
        #self.assertEqual(sg.facilitator_goal_rating, None)


    def test_course_page(self):
        course = Course.objects.get(pk=3)

        c = Client()
        response = c.get('/en/course/{}/'.format(course.id))

        self.assertEqual(response.status_code, 200)

        expected_create_studygroup_url = reverse('studygroups_facilitator_studygroup_create') + "?course_id={}".format(course.id)
        expected_rating_step_counts = json.loads(course.rating_step_counts)
        expected_generate_discourse_topic_url = reverse('studygroups_generate_course_discourse_topic', args=(course.id,))

        self.assertEqual(response.context_data['usage'], 1)
        self.assertIsNotNone(response.context_data['rating_counts_chart'])
        self.assertEqual(response.context_data['rating_step_counts'], expected_rating_step_counts)
        self.assertEqual(len(json.loads(response.context_data['similar_courses'])), 3)
        self.assertIn(expected_create_studygroup_url, str(response.content))
        self.assertIn(expected_generate_discourse_topic_url, str(response.content))


    @patch('studygroups.views.facilitate.create_discourse_topic')
    def test_generate_course_discourse_topic(self, mock_request):
        course = Course.objects.get(pk=3)
        url = reverse('studygroups_generate_course_discourse_topic', args=(course.id,))

        mock_slug = "test-slug"
        mock_id = "123"
        mock_url = "{}/t/{}/{}".format("https://community.p2pu.org", mock_slug, mock_id)
        mock_response = {
            "topic_slug": mock_slug,
            "topic_id": mock_id
        }
        mock_request.configure_mock(return_value=mock_response)

        c = Client()
        response = c.get(url)

        self.assertRedirects(response, mock_url, fetch_redirect_response=False)


    @patch('studygroups.views.facilitate.create_discourse_topic')
    def test_generate_course_discourse_topic_failure(self, mock_request):
        course = Course.objects.get(pk=3)
        url = reverse('studygroups_generate_course_discourse_topic', args=(course.id,))

        mock_slug = "test-slug"
        mock_id = "123"
        mock_url = "{}/t/{}/{}".format("https://community.p2pu.org", mock_slug, mock_id)
        mock_response = {
            "topic_slug": mock_slug,
            "topic_id": mock_id
        }
        mock_request.configure_mock(return_value=mock_response)
        mock_request.side_effect = Exception('Mock Exception')

        expected_redirect_url = "{}/c/learning-circles/courses-and-topics".format(settings.DISCOURSE_BASE_URL)

        c = Client()
        response = c.get(url)

        self.assertRedirects(response, expected_redirect_url, fetch_redirect_response=False)



