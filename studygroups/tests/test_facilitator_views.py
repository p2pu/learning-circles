# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language
from django.urls import reverse

from mock import patch
from freezegun import freeze_time

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import Rsvp
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import Feedback
from studygroups.models import generate_all_meetings
from studygroups.rsvp import gen_rsvp_querystring
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
        'use_internet': '2'
    }

    STUDY_GROUP_DATA = {
        'course': '1',
        'venue_name': 'мой дом',
        'venue_details': 'Garrage at my house',
        'venue_address': 'Rosemary Street 6',
        'city': 'Johannesburg',
        'latitude': -26.205,
        'longitude': 28.0497,
        'place_id': '342432',
        'description': 'We will complete the course about motorcycle maintenance together',
        'start_date': '2016-07-25',
        'weeks': '6',
        'meeting_time': '19:00',
        'duration': '90',
        'timezone': 'Africa/Johannesburg',
        'venue_website': 'http://venue.com',
    }

    def setUp(self):
        user = User.objects.create_user('admin', 'admin@test.com', 'password')
        user.is_superuser = True
        user.is_staff = True
        user.save()


    def test_user_forbidden(self):
        user = User.objects.create_user('bob', 'bob@example.net', 'password')
        c = Client()
        c.login(username='bob', password='password')
        def assertForbidden(url):
            resp = c.get(url)
            self.assertEqual(resp.status_code, 403)
        assertForbidden('/en/organize/')
        assertForbidden('/en/report/weekly/')
        assertForbidden('/en/studygroup/1/')
        assertForbidden('/en/studygroup/1/edit/')
        assertForbidden('/en/studygroup/1/message/compose/')
        assertForbidden('/en/studygroup/1/message/edit/1/')
        assertForbidden('/en/studygroup/1/member/add/')
        assertForbidden('/en/studygroup/1/member/1/delete/')
        assertForbidden('/en/studygroup/1/meeting/create/')
        assertForbidden('/en/studygroup/1/meeting/2/edit/')
        assertForbidden('/en/studygroup/1/meeting/2/delete/')
        assertForbidden('/en/studygroup/1/meeting/2/feedback/create/')
        assertForbidden('/en/studygroup/1/facilitator_survey/')


    def test_facilitator_access(self):
        User.objects.create_user('bob123', 'bob@example.net', 'password')
        user = User.objects.get(username='bob123')
        sg = StudyGroup.objects.get(pk=1)
        sg.facilitator = user
        sg.save()
        c = Client()
        c.login(username='bob123', password='password')
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
        assertStatus('/en/studygroup/1/message/edit/1/', 404)
        assertAllowed('/en/studygroup/1/member/add/')
        assertStatus('/en/studygroup/1/member/2/delete/', 404)
        assertAllowed('/en/studygroup/1/meeting/create/')
        assertStatus('/en/studygroup/1/meeting/2/edit/', 404)
        assertStatus('/en/studygroup/1/meeting/2/delete/', 404)
        assertStatus('/en/studygroup/1/meeting/2/feedback/create/', 404)
        assertAllowed('/en/studygroup/1/facilitator_survey/')


    def test_create_study_group(self):
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
        c = Client()
        c.login(username='bob123', password='password')
        data = self.STUDY_GROUP_DATA.copy()
        data['start_date'] = '07/25/2016',
        data['meeting_time'] = '07:00 PM',
        resp = c.post('/en/studygroup/create/legacy/', data)
        self.assertRedirects(resp, '/en/facilitator/')
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEquals(study_groups.count(), 1)
        lc = study_groups.first()
        self.assertEquals(study_groups.first().meeting_set.count(), 0)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your “{}” learning circle in {} has been created! What next?'.format(lc.course.title, lc.city))
        self.assertIn('bob@example.net', mail.outbox[0].to)
        self.assertIn('community@localhost', mail.outbox[0].cc)


    @patch('custom_registration.signals.handle_new_facilitator')
    def test_publish_study_group(self, handle_new_facilitator):
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        confirm_user_email(user)
        c = Client()
        c.login(username='bob@example.net', password='password')

        resp = c.post('/api/learning-circle/', data=json.dumps(self.STUDY_GROUP_DATA), content_type='application/json')
        self.assertEqual(resp.json()['status'], 'created')
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEqual(study_groups.count(), 1)
        self.assertEqual(study_groups.first().meeting_set.count(), 0)

        resp = c.post('/en/studygroup/{0}/publish/'.format(study_groups.first().pk))
        self.assertRedirects(resp, '/en/facilitator/')
        study_group = StudyGroup.objects.get(pk=study_groups.first().pk)
        self.assertEqual(study_group.draft, False)
        self.assertEqual(study_group.meeting_set.count(), 6)


    @patch('custom_registration.signals.handle_new_facilitator')
    def test_publish_study_group_email_unconfirmed(self, handle_new_facilitator):
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        c = Client()
        c.login(username='bob@example.net', password='password')

        resp = c.post('/api/learning-circle/', data=json.dumps(self.STUDY_GROUP_DATA), content_type='application/json')
        self.assertEqual(resp.json()['status'], 'created')
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEqual(study_groups.count(), 1)

        resp = c.post('/en/studygroup/{0}/publish/'.format(study_groups.first().pk))
        self.assertRedirects(resp, '/en/facilitator/')
        study_group = StudyGroup.objects.get(pk=study_groups.first().pk)
        self.assertEqual(study_group.draft, True)


    @patch('custom_registration.signals.handle_new_facilitator')
    def test_draf_study_group_actions_disabled(self, handle_new_facilitator):
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        confirm_user_email(user)
        c = Client()
        c.login(username='bob@example.net', password='password')

        resp = c.post('/api/learning-circle/', data=json.dumps(self.STUDY_GROUP_DATA), content_type='application/json')
        self.assertEqual(resp.json()['status'], 'created')
        study_groups = StudyGroup.objects.filter(facilitator=user)
        self.assertEqual(study_groups.count(), 1)
        self.assertEqual(study_groups.first().meeting_set.count(), 0)

        # try to add a meeting
        self.assertEqual(study_groups.first().pk, StudyGroup.objects.last().pk)
        url_base = '/en/studygroup/{0}'.format(study_groups.first().pk)
        resp = c.get(url_base + '/meeting/create/')
        self.assertRedirects(resp, '/en/facilitator/')
        meeting_data = {
            "meeting_date": "2018-03-17",
            "meeting_time": "04:00+PM",
            "study_group": "515",
        }
        resp = c.post(url_base + '/meeting/create/', data=meeting_data)
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(StudyGroup.objects.last().meeting_set.count(), 0)

        # try to send a message
        resp = c.get('/en/studygroup/{0}/message/compose/'.format(study_groups.first().pk))
        self.assertRedirects(resp, '/en/facilitator/')
        mail_data = {
            u'study_group': study_groups.first().pk,
            u'email_subject': 'does not matter',
            u'email_body': 'does not matter',
        }
        mail.outbox = []
        resp = c.post(url_base + '/message/compose/', mail_data)
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(len(mail.outbox), 0)

        # try to add a learner
        resp = c.get('/en/studygroup/{0}/member/add/'.format(study_groups.first().pk))
        self.assertRedirects(resp, '/en/facilitator/')
        learner_data = {
            "email": "learn@example.net",
            "name": "no name",
            "study_group": "515",
        }
        resp = c.post(url_base + '/member/add/', data=learner_data)
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(StudyGroup.objects.last().application_set.count(), 0)


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
        self.assertEqual(study_groups.count(), 1)
        self.assertEqual(study_groups.first().meeting_set.count(), 6)

        resp = c.get('/en/facilitator/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('/en/signup/%D0%B1%D1%8B%D1%81%D1%82%D1%80%D0%B5%D0%B5-%D0%B8-%D0%BB%D1%83%D1%87%D1%88%D0%B5-', resp.content.decode("utf-8"))



    @patch('studygroups.models.send_message')
    def test_send_email(self, send_message):
        # Test sending a message
        c = Client()
        c.login(username='admin', password='password')
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
        self.assertRedirects(resp, '/en/facilitator/')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, mail_data['email_subject'])
        self.assertEqual(mail.outbox[0].from_email, 'Facilitator1 <webmaster@localhost>')
        self.assertFalse(send_message.called)
        self.assertIn('https://example.net/en/optout/', mail.outbox[0].body)


    @patch('studygroups.models.send_message')
    def test_send_sms(self, send_message):
        c = Client()
        c.login(username='admin', password='password')
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
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(len(mail.outbox), 1)  # Send both email and text message
        self.assertTrue(send_message.called)


    @patch('studygroups.models.send_message')
    def test_dont_send_blank_sms(self, send_message):
        c = Client()
        c.login(username='admin', password='password')
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
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(len(mail.outbox), 1)  # Still send email
        self.assertFalse(send_message.called) # dont send sms


    def test_feedback_submit(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', '1234')
        faci1 = User.objects.create_user('faci1@team.com', 'faci1@team.com', '1234')
        StudyGroup.objects.filter(pk=1).update(facilitator=faci1)

        # create team
        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        TeamMembership.objects.create(team=team, user=faci1, role=TeamMembership.MEMBER)


        c = Client()
        c.login(username='faci1@team.com', password='1234')
        study_group = StudyGroup.objects.get(pk=1)
        meeting = Meeting()
        meeting.study_group = study_group
        meeting.meeting_time = timezone.now().time()
        meeting.meeting_date = timezone.now().date() - datetime.timedelta(days=1)
        meeting.save()

        feedback_data = {
            'study_group_meeting': '{0}'.format(meeting.id),
            'feedback': 'Test some feedback',
            'reflection': 'Please help me',
            'attendance': '9',
            'rating': '5',
        }
        feedback_url = '/en/studygroup/1/meeting/{0}/feedback/create/'.format(meeting.id)
        self.assertEqual(len(mail.outbox), 0)
        resp = c.post(feedback_url, feedback_data)
        self.assertEqual(resp.status_code, 302)
        # make sure email was sent to organizers
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Feedback.objects.filter(study_group_meeting=meeting).count(), 1)


    def test_user_accept_invitation(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', '1234')
        faci1 = User.objects.create_user('faci1@team.com', 'faci1@team.com', '1234')
        StudyGroup.objects.filter(pk=1).update(facilitator=faci1)

        # create team
        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)

        c = Client()
        c.login(username='faci1@team.com', password='1234')
        resp = c.get('/en/facilitator/team-invitation/')
        self.assertRedirects(resp, '/en/facilitator/')

        TeamInvitation.objects.create(team=team, organizer=organizer, role=TeamMembership.MEMBER, email=faci1.email)
        self.assertTrue(TeamInvitation.objects.get(team=team, role=TeamMembership.MEMBER, email__iexact=faci1.email).responded_at is None)
        resp = c.post('/en/facilitator/team-invitation/', {'response': 'yes'})
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(TeamMembership.objects.filter(team=team, role=TeamMembership.MEMBER, user=faci1).count(), 1)
        self.assertFalse(TeamInvitation.objects.get(team=team, role=TeamMembership.MEMBER, email__iexact=faci1.email).responded_at is None)


    def test_user_rejept_invitation(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', '1234')
        faci1 = User.objects.create_user('faci1@team.com', 'faci1@team.com', '1234')
        StudyGroup.objects.filter(pk=1).update(facilitator=faci1)

        # create team
        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)

        c = Client()
        c.login(username='faci1@team.com', password='1234')

        TeamInvitation.objects.create(team=team, organizer=organizer, role=TeamMembership.MEMBER, email=faci1.email)
        self.assertTrue(TeamInvitation.objects.get(team=team, role=TeamMembership.MEMBER, email__iexact=faci1.email).responded_at is None)
        resp = c.post('/en/facilitator/team-invitation/', {'response': 'no'})
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(TeamMembership.objects.filter(team=team, role=TeamMembership.MEMBER, user=faci1).count(), 0)
        self.assertFalse(TeamInvitation.objects.get(team=team, role=TeamMembership.MEMBER, email__iexact=faci1.email).responded_at is None)


    def test_edit_course(self):
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
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
        c.login(username='bob123', password='password')
        # make sure bob123 can edit the course
        course_url = '/en/course/{}/edit/'.format(course.id)
        resp = c.get(course_url)
        course_data['topics'] = 'magic'
        resp = c.post(course_url, course_data)
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(Course.objects.get(pk=course.id).topics, 'magic')


    def test_cant_edit_other_facilitators_course(self):
        User.objects.create_user('bob321', 'bob2@example.net', 'password')
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
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
        c.login(username='bob321', password='password')
        course_url = '/en/course/{}/edit/'.format(course.id)
        resp = c.get(course_url)
        self.assertEqual(resp.status_code, 403)
        course_data['topics'] = 'magic'
        resp = c.post(course_url, course_data)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Course.objects.get(pk=course.id).topics, 'html,test')


    def test_cant_edit_used_course(self):
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
        user2 = User.objects.create_user('bob1234', 'bob2@example.net', 'password')
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
        c.login(username='bob123', password='password')
        # make sure bob123 can edit the course
        course_url = '/en/course/{}/edit/'.format(course.id)
        resp = c.get(course_url)
        self.assertRedirects(resp, '/en/facilitator/')
        course_data['topics'] = 'magic'
        resp = c.post(course_url, course_data)
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(Course.objects.get(pk=course.id).topics, 'html,test')


    def test_study_group_facilitator_survey(self):
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
        c = Client()
        c.login(username='bowie', password='password')
        feedback_url = '/en/studygroup/{}/facilitator_survey/?rating=5'.format(sg.pk)
        response = c.get(feedback_url)

        sg.refresh_from_db()
        self.assertEqual(sg.facilitator_rating, 5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['study_group_uuid'], sg.uuid)
        self.assertEqual(response.context_data['study_group_name'], course.title)
        self.assertEqual(response.context_data['facilitator'], facilitator)
        self.assertEqual(response.context_data['facilitator_name'], facilitator.first_name)

    def test_facilitator_active_learning_circles(self):
        facilitator = User.objects.create_user('bowie', 'hi@example.net', 'password')
        sg = StudyGroup.objects.get(pk=1)
        sg.facilitator = facilitator
        sg.start_date = datetime.date(2018, 5, 24)
        sg.end_date = datetime.date(2018, 5, 24) + datetime.timedelta(weeks=5)
        sg.draft = True
        sg.save()
        sg.meeting_set.delete()
        c = Client()

        with freeze_time("2018-05-02"):
            c.login(username='bowie', password='password')
            resp = c.get('/en/facilitator/')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(sg, resp.context['current_study_groups'])

        sg.draft = False
        sg.save()
        generate_all_meetings(sg)

        with freeze_time("2018-05-02"):
            c.login(username='bowie', password='password')
            resp = c.get('/en/facilitator/')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(sg, resp.context['current_study_groups'])

        with freeze_time("2018-07-16"):
            c.login(username='bowie', password='password')
            resp = c.get('/en/facilitator/')
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(sg, resp.context['current_study_groups'])


