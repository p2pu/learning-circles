# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language

from mock import patch

from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import Rsvp
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import Feedback
from studygroups.rsvp import gen_rsvp_querystring

import datetime
import urllib.request, urllib.parse, urllib.error
import json


"""
Tests for when organizers interact with the system
"""
class TestOrganizerViews(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']


    def setUp(self):
        user = User.objects.create_user('admin', 'admin@test.com', 'password')
        user.is_superuser = True
        user.is_staff = True
        user.save()


    def test_organizer_login_redirect(self):
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=user, role=TeamMembership.ORGANIZER)
        c = Client()
        c.login(username='bob123', password='password')
        resp = c.get('/en/login_redirect/')
        self.assertRedirects(resp, '/en/organize/{}/'.format(team.pk))


    def test_organizer_access(self):
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
        faci1 = User.objects.create_user('faci1@team.com', 'faci1@team.com', '1234')

        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=user, role=TeamMembership.ORGANIZER)
        TeamMembership.objects.create(team=team, user=faci1, role=TeamMembership.MEMBER)

        sg = StudyGroup.objects.get(pk=1)
        sg.facilitator = faci1
        sg.save()

        c = Client()
        c.login(username='bob123', password='password')

        def assertAllowed(url):
            resp = c.get(url)
            self.assertIn(resp.status_code, [200, 301, 302])

        def assertStatus(url, status):
            resp = c.get(url)
            self.assertEqual(resp.status_code, status)

        def assertForbidden(url):
            resp = c.get(url)
            self.assertEqual(resp.status_code, 403)

        assertAllowed('/en/')
        assertAllowed('/en/organize/')
        assertAllowed('/en/organize/{}/'.format(team.pk))
        assertAllowed('/en/report/weekly/')

        # Make sure the organizer can access their study groups
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

        # Make sure the organizer can't access other study groups
        assertForbidden('/en/organize/{}/'.format(team.pk + 1))
        assertForbidden('/en/studygroup/2/')
        assertForbidden('/en/studygroup/2/edit/')
        assertForbidden('/en/studygroup/2/message/compose/')
        assertForbidden('/en/studygroup/2/message/edit/1/')
        assertForbidden('/en/studygroup/2/member/add/')
        assertForbidden('/en/studygroup/2/member/2/delete/')
        assertForbidden('/en/studygroup/2/meeting/create/')
        assertForbidden('/en/studygroup/2/meeting/2/edit/')
        assertForbidden('/en/studygroup/2/meeting/2/delete/')
        assertForbidden('/en/studygroup/2/meeting/2/feedback/create/')


    def test_staff_access(self):
        c = Client()
        c.login(username='admin', password='password')

        def assertAllowed(url):
            resp = c.get(url)
            self.assertIn(resp.status_code, [200, 301, 302])

        def assertStatus(url, status):
            resp = c.get(url)
            self.assertEqual(resp.status_code, status)

        def assertForbidden(url):
            resp = c.get(url)
            self.assertEqual(resp.status_code, 403)

        assertAllowed('/en/')
        assertAllowed('/en/organize/')
        assertAllowed('/en/report/weekly/')

        # Make sure staff can access study groups
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


    def test_organizer_dash(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', '1234')
        faci1 = User.objects.create_user('faci1@team.com', 'faci1@team.com', '1234')
        faci2 = User.objects.create_user('faci2@team.com', 'faci2@team.com', '1234')

        sg = StudyGroup.objects.get(pk=1)
        sg.facilitator = faci1
        sg.save()

        sg = StudyGroup.objects.get(pk=2)
        sg.facilitator = faci2
        sg.save()
        
        # create team
        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        TeamMembership.objects.create(team=team, user=faci1, role=TeamMembership.MEMBER)
        TeamMembership.objects.create(team=team, user=faci2, role=TeamMembership.MEMBER)

        c = Client()
        c.login(username='organ@team.com', password='1234')
        resp = c.get('/en/organize/')
        self.assertRedirects(resp, '/en/organize/{}/'.format(team.pk))

        resp = c.get('/en/organize/{}/'.format(team.pk))
        self.assertEqual(resp.status_code, 200)
        # make sure only the relevant study groups are returned
        self.assertEqual(len(resp.context['study_groups']), 2)
        self.assertIn(StudyGroup.objects.get(pk=1), resp.context['study_groups'])
        self.assertIn(StudyGroup.objects.get(pk=2), resp.context['study_groups'])


    def test_organizer_dash_for_staff(self):
        c = Client()
        c.login(username='admin', password='password')
        resp = c.get('/en/organize/')
        self.assertEqual(resp.status_code, 200)

        # make sure all study groups are returned
        self.assertEqual(StudyGroup.objects.active().count(), len(resp.context['study_groups']))


    def test_weekly_report(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', 'password')
        faci1 = User.objects.create_user('faci1@team.com', 'faci1@team.com', 'password')
        StudyGroup.objects.filter(pk=1).update(facilitator=faci1)
        StudyGroup.objects.filter(pk=3).update(facilitator=faci1)
        StudyGroup.objects.filter(pk=3).update(deleted_at=timezone.now())

        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        TeamMembership.objects.create(team=team, user=faci1, role=TeamMembership.MEMBER)

        study_group = StudyGroup.objects.get(pk=1)
        active_meeting = Meeting.objects.create(
            study_group = study_group,
            meeting_time = datetime.time(16, 0),
            meeting_date = datetime.date(2016, 11, 24)  # Thursday
        )

        study_group = StudyGroup.objects.get(pk=2)
        meeting = Meeting()
        meeting.study_group = study_group
        meeting.meeting_time = datetime.time(16, 0)
        meeting.meeting_date = datetime.date(2016, 11, 25)  # Thursday
        meeting.save()

        Meeting.objects.create(
            study_group = StudyGroup.objects.get(pk=3),
            meeting_time = datetime.time(16, 0),
            meeting_date = datetime.date(2016, 11, 21)  # Monday
        )
 
        c = Client()
        c.login(username='organ@team.com', password='password')
        resp = c.get('/en/report/weekly/{0}/'.format(datetime.date(2016, 11, 21).strftime("%Y-%m-%d")))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['meetings']), 1)
        self.assertEqual(resp.context['meetings'][0].pk, active_meeting.pk)
        #TODO test other parts of the weekly report


    def test_invite_new_user(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', 'password')
        organizer.first_name = 'Orgaborga'
        organizer.save()
        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        
        c = Client()
        c.login(username='organ@team.com', password='password')
        invite_url = '/en/organize/team/{0}/member/invite/'.format(team.pk)
        resp = c.post(invite_url, json.dumps({"email":"hume@team.com"}), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        
        self.assertEqual(TeamInvitation.objects.filter(team=team).count(),1)
        self.assertEqual(len(mail.outbox), 1)
        # Make sure correct email was sent
        self.assertIn('sign up', mail.outbox[0].body)
        self.assertIn('Orgaborga', mail.outbox[0].body)


    def test_invite_existing_user(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', 'password')
        organizer.first_name = 'Orgaborga'
        organizer.save()
        faci1 = User.objects.create_user('faci1@team.com', 'faci1@team.com', 'password')
        faci1.first_name = 'Bobobob'
        faci1.save()

        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        
        c = Client()
        c.login(username='organ@team.com', password='password')
        invite_url = '/en/organize/team/{0}/member/invite/'.format(team.pk)
        resp = c.post(invite_url, json.dumps({"email":"faci1@team.com"}), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(TeamInvitation.objects.filter(team=team).count(),1)
        self.assertEqual(len(mail.outbox), 1)
        # Make sure correct email was sent
        self.assertIn('Bobobob', mail.outbox[0].body)
        self.assertIn('Orgaborga', mail.outbox[0].body)


    def test_invite_existing_user_with_email_mixed_case(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', 'password')
        organizer.first_name = 'Orgaborga'
        organizer.save()
        faci1 = User.objects.create_user('faci1@team.com', 'fAcI1@team.com', 'password')
        faci1.first_name = 'Bobobob'
        faci1.save()

        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        
        c = Client()
        c.login(username='organ@team.com', password='password')
        invite_url = '/en/organize/team/{0}/member/invite/'.format(team.pk)
        resp = c.post(invite_url, json.dumps({"email":"faCi1@team.com"}), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'CREATED')
        self.assertEqual(TeamInvitation.objects.filter(team=team).count(),1)
        self.assertEqual(len(mail.outbox), 1)
        # Make sure correct email was sent
        self.assertIn('Bobobob', mail.outbox[0].body)
        self.assertIn('Orgaborga', mail.outbox[0].body)



    def test_only_group_organizer_can_invite(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', 'password')
        organizer.first_name = 'Orgaborga'
        organizer.save()
        team = Team.objects.create(name='test team')
        team2 = Team.objects.create(name='test team 2')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        
        c = Client()
        c.login(username='organ@team.com', password='password')
        invite_url = '/en/organize/team/{0}/member/invite/'.format(team2.pk)
        resp = c.post(invite_url, json.dumps({"email":"hume@team.com"}), content_type="application/json")
        self.assertEqual(resp.status_code, 403)


    def test_valid_invite(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', 'password')
        organizer.first_name = 'Orgaborga'
        organizer.save()
        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        
        c = Client()
        c.login(username='organ@team.com', password='password')
        invite_url = '/en/organize/team/{0}/member/invite/'.format(team.pk)
        resp = c.post(invite_url, json.dumps({"email":"humemail.mail"}), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('status'), 'ERROR')

