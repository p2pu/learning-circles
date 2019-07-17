from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import get_language
from django.conf import settings
from django.urls import reverse

from mock import patch
from freezegun import freeze_time

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import Rsvp
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import accept_application
from studygroups.models import create_rsvp
from studygroups.models import generate_all_meetings
from studygroups.utils import gen_rsvp_querystring
from studygroups.utils import check_rsvp_signature
from studygroups.utils import gen_unsubscribe_querystring
from studygroups.utils import check_unsubscribe_signature

from studygroups.tasks import generate_reminder
from studygroups.tasks import send_reminders
from studygroups.tasks import send_reminder
from studygroups.tasks import send_weekly_update
from studygroups.tasks import send_learner_surveys
from studygroups.tasks import send_facilitator_survey
from studygroups.tasks import send_facilitator_learner_survey_prompt
from studygroups.tasks import send_final_learning_circle_report
from studygroups.tasks import send_last_week_group_activity
from studygroups.tasks import send_out_community_digest

import calendar
import datetime
import pytz
import re
import urllib.request, urllib.parse, urllib.error
import json



# Create your tests here.
class TestStudyGroupTasks(TestCase):

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
        user = User.objects.create_user('admin', 'admin@test.com', 'password')
        user.is_staff = True
        user.save()


    def test_dont_generate_reminder_4days_before(self):
        # Make sure we don't generate a reminder more than 4 days before
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = now + datetime.timedelta(days=4, hours=1)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 0)


    def test_generate_reminder_4days_before(self):
        # Make sure we generate a reminder less than 4 days before
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = now.date() + datetime.timedelta(days=3)
        sg.meeting_time = now.time()
        sg.end_date = now.date() + datetime.timedelta(weeks=5, days=3)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)
        self.assertEqual(sg.meeting_set.active().count(), 6)
        self.assertTrue(sg.next_meeting().meeting_datetime() - now < datetime.timedelta(days=4))
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        #TODO check that email was sent to site admin
        #TODO test with unicode in generated email subject

        # Make sure we do it only once
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)

    def test_no_reminders_for_old_studygroups(self):
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)

        # Make sure we don't generate a reminder for old study groups
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = now - datetime.timedelta(days=5, weeks=7)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 0)


    def test_no_reminders_for_future_studygroups(self):
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)

        # Make sure we don't generate a reminder for future study groups
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = now + datetime.timedelta(days=2, weeks=1)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 0)

    def test_generate_reminder_with_long_name_and_location(self):
        # Make sure we generate a reminder less than 4 days before
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.venue_name = 'This is a very long venue name to test for sms reminders that are longer than a 160 caracters long'
        sg.venue_details = 'This is an even longer venue detail field. I am almost 100% certain this will be cut off. What do you think'
        sg.start_date = now.date() + datetime.timedelta(days=3)
        sg.meeting_time = now.time()
        sg.end_date = now.date() + datetime.timedelta(weeks=5, days=3)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)
        self.assertEqual(sg.meeting_set.active().count(), 6)
        self.assertTrue(sg.next_meeting().meeting_datetime() - now < datetime.timedelta(days=4))
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        #TODO check that email was sent to site admin
        #TODO test with unicode in generated email subject

        # Make sure we do it only once
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)


    @patch('studygroups.tasks.send_message')
    def test_dont_send_automatic_reminder_for_old_message(self, send_message):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = datetime.date(2010, 3, 10)
        sg.meeting_time = datetime.time(18,0)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)

        data = self.APPLICATION_DATA
        data['study_group'] = sg
        application = Application(**data)
        application.save()
        accept_application(application)

        mail.outbox = []
        with freeze_time("2010-03-06 18:55:34"):
            generate_reminder(sg)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Reminder.objects.all().count(), 1)

        mail.outbox = []
        with freeze_time("2010-03-08 18:55:34"):
            send_reminders()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to[0], data['email'])
        self.assertEqual(mail.outbox[1].to[0], 'facilitator@example.net')
        self.assertFalse(send_message.called)
        self.assertEqual(Reminder.objects.filter(sent_at__isnull=True).count(), 0)

        mail.outbox = []
        with freeze_time("2010-03-13 18:55:34"):
            generate_reminder(sg)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(Reminder.objects.all().count(), 2)
        self.assertEqual(Reminder.objects.filter(sent_at__isnull=True).count(), 1)

        reminder = Reminder.objects.filter(sent_at__isnull=True).first()
        self.assertEqual(reminder.study_group_meeting.meeting_date, datetime.date(2010, 3, 17))

        mail.outbox = []
        with freeze_time("2010-03-18 18:55:34"):
            send_reminders()
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Reminder.objects.filter(sent_at__isnull=True).count(), 1)


    @patch('studygroups.tasks.send_message')
    def test_send_automatic_reminder_email(self, send_message):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = now - datetime.timedelta(days=5)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        data = self.APPLICATION_DATA
        data['study_group'] = sg
        application = Application(**data)
        accept_application(application)
        application.save()
        mail.outbox = []
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        self.assertEqual(len(mail.outbox), 1)
        send_reminder(reminder)
        self.assertEqual(len(mail.outbox), 3) # should be sent to facilitator & application
        self.assertEqual(mail.outbox[1].to[0], data['email'])
        self.assertFalse(send_message.called)
        self.assertIn('{0}/{1}/rsvp/?user=test%40mail.com&study_group=1&meeting_date={2}&attending=yes&sig='.format(settings.DOMAIN, get_language(), urllib.parse.quote(sg.next_meeting().meeting_datetime().isoformat())), mail.outbox[1].alternatives[0][0])
        self.assertIn('{0}/{1}/rsvp/?user=test%40mail.com&study_group=1&meeting_date={2}&attending=no&sig='.format(settings.DOMAIN, get_language(), urllib.parse.quote(sg.next_meeting().meeting_datetime().isoformat())), mail.outbox[1].alternatives[0][0])
        self.assertIn('{0}/{1}/optout/confirm/?user='.format(settings.DOMAIN, get_language()), mail.outbox[1].alternatives[0][0])


    @patch('studygroups.tasks.send_message')
    def test_send_learner_reminder_ics(self, send_message):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = now - datetime.timedelta(days=5)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.attach_ics = True
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        data = self.APPLICATION_DATA
        data['study_group'] = sg
        application = Application(**data)
        accept_application(application)
        application.save()
        mail.outbox = []
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        self.assertEqual(len(mail.outbox), 1)
        send_reminder(reminder)
        self.assertEqual(len(mail.outbox), 3) # should be sent to facilitator & application
        self.assertEqual(mail.outbox[1].to[0], data['email'])
        self.assertFalse(send_message.called)
        self.assertIn('{0}/{1}/rsvp/?user=test%40mail.com&study_group=1&meeting_date={2}&attending=yes&sig='.format(settings.DOMAIN, get_language(), urllib.parse.quote(sg.next_meeting().meeting_datetime().isoformat())), mail.outbox[1].alternatives[0][0])
        self.assertIn('{0}/{1}/rsvp/?user=test%40mail.com&study_group=1&meeting_date={2}&attending=no&sig='.format(settings.DOMAIN, get_language(), urllib.parse.quote(sg.next_meeting().meeting_datetime().isoformat())), mail.outbox[1].alternatives[0][0])
        self.assertIn('{0}/{1}/optout/confirm/?user='.format(settings.DOMAIN, get_language()), mail.outbox[1].alternatives[0][0])
        self.assertIn('VEVENT', mail.outbox[1].attachments[0].get_payload())


    @patch('studygroups.tasks.send_message')
    def test_send_custom_reminder_email(self, send_message):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = now - datetime.timedelta(days=5)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)

        data = self.APPLICATION_DATA
        data['study_group'] = sg
        application = Application(**data)
        accept_application(application)
        application.save()
        mail.outbox = []
        generate_all_meetings(sg)

        reminder = Reminder(
            study_group=sg,
            email_subject='Custom reminder',
            email_body='Test for extra reminders sent by facilitators',
            sms_body='Nothing to say here'
        )
        reminder.save()
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        self.assertEqual(len(mail.outbox), 0)
        send_reminder(reminder)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].bcc), 2)
        self.assertEqual(mail.outbox[0].bcc[0], data['email'])
        self.assertFalse(send_message.called)
        #self.assertIn('https://example.net/{0}/optout/confirm/?user='.format(get_language()), mail.outbox[0].body)


    @patch('studygroups.tasks.send_message')
    def test_facilitator_reminder_email_links(self, send_message):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = now - datetime.timedelta(days=5)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        data = self.APPLICATION_DATA
        data['study_group'] = sg
        application = Application(**data)
        accept_application(application)
        application.save()
        mail.outbox = []
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        self.assertEqual(len(mail.outbox), 1)
        mail.outbox = []
        send_reminder(reminder)
        self.assertEqual(len(mail.outbox), 2) # should be sent to facilitator & application
        self.assertEqual(mail.outbox[0].to[0], data['email'])
        self.assertEqual(mail.outbox[1].to[0], sg.facilitator.email)
        self.assertFalse(send_message.called)
        self.assertNotIn('{0}/{1}/rsvp/'.format(settings.DOMAIN, get_language()), mail.outbox[1].alternatives[0][0])
        self.assertIn('{0}/{1}/'.format(settings.DOMAIN, get_language()), mail.outbox[1].alternatives[0][0])
        self.assertNotIn('{0}/{1}/optout/confirm/?user='.format(settings.DOMAIN, get_language()), mail.outbox[1].alternatives[0][0])


    @patch('studygroups.tasks.send_message')
    def test_send_reminder_sms(self, send_message):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = now - datetime.timedelta(days=5)
        sg.meeting_time = sg.start_date.time()
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        data = self.APPLICATION_DATA
        data['study_group'] = sg
        application = Application(**data)
        application.save()
        mail.outbox = []
        generate_all_meetings(sg)
        generate_reminder(sg)
        self.assertEqual(Reminder.objects.all().count(), 1)
        reminder = Reminder.objects.all()[0]
        send_reminder(reminder)
        self.assertEqual(len(mail.outbox), 2)
        #self.assertEqual(mail.outbox[0].subject, mail_data['email_subject'])
        self.assertFalse(send_message.called)


    def test_send_weekly_report(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', 'password')
        faci1 = User.objects.create_user('faci1@team.com', 'faci1@team.com', 'password')
        StudyGroup.objects.filter(pk=1).update(facilitator=faci1)

        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        TeamMembership.objects.create(team=team, user=faci1, role=TeamMembership.MEMBER)

        study_group = StudyGroup.objects.get(pk=1)
        meeting = Meeting()
        meeting.study_group = study_group
        meeting.meeting_time = datetime.time(9)
        meeting.meeting_date = datetime.date(2018, 8, 22)
        meeting.save()

        study_group = StudyGroup.objects.get(pk=2)
        meeting = Meeting()
        meeting.study_group = study_group
        meeting.meeting_time = datetime.time(9)
        meeting.meeting_date = datetime.date(2018, 8, 22)
        meeting.save()


        with freeze_time("2018-08-28 10:01:00"):
            send_weekly_update()

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].cc[0], 'faci1@team.com')
        self.assertEqual(mail.outbox[0].cc[1], 'organ@team.com')
        self.assertEqual(mail.outbox[1].to[0], 'admin@test.com')


    def test_dont_send_weekly_report(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', 'password')
        faci1 = User.objects.create_user('faci1@team.com', 'faci1@team.com', 'password')
        StudyGroup.objects.filter(pk=1).update(facilitator=faci1)

        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        TeamMembership.objects.create(team=team, user=faci1, role=TeamMembership.MEMBER)

        study_group = StudyGroup.objects.get(pk=1)
        meeting = Meeting()
        meeting.study_group = study_group
        meeting.meeting_time = datetime.time(9)
        meeting.meeting_date = datetime.date(2018, 8, 14)
        meeting.save()

        study_group = StudyGroup.objects.get(pk=2)
        meeting = Meeting()
        meeting.study_group = study_group
        meeting.meeting_time = datetime.time(9)
        meeting.meeting_date = datetime.date(2018, 8, 14)
        meeting.save()

        with freeze_time("2018-08-28 10:01:00"):
            send_weekly_update()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], 'admin@test.com')


    def test_send_learner_surveys(self):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = datetime.date(2010, 1, 1)
        sg.meeting_time = datetime.time(18,0)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=6)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)

        data = dict(self.APPLICATION_DATA)
        data['study_group'] = sg
        data['email'] = 'mail1@example.net'
        application = Application(**data)
        application.save()
        accept_application(application)

        data = dict(self.APPLICATION_DATA)
        data['study_group'] = sg
        data['email'] = 'mail2@example.net'
        application = Application(**data)
        accept_application(application)
        application.save()

        mail.outbox = []

        last_meeting = sg.meeting_set.active().order_by('meeting_date', 'meeting_time').last()
        self.assertEqual(last_meeting.meeting_date, datetime.date(2010, 2, 12))
        self.assertEqual(last_meeting.meeting_time, datetime.time(18))
        self.assertEqual(sg.meeting_set.active().count(), 7)
        self.assertEqual(sg.application_set.active().count(), 2)

        # too soon
        with freeze_time("2010-02-12 16:30:00"):
            send_learner_surveys(sg)
            self.assertEqual(len(mail.outbox), 0)

        # too late
        with freeze_time("2010-02-12 18:30:00"):
            send_learner_surveys(sg)
            self.assertEqual(len(mail.outbox), 0)

        with freeze_time("2010-02-12 17:30:00"):
            send_learner_surveys(sg)
            self.assertEqual(len(mail.outbox), 2)
            self.assertIn('mail1@example.net', mail.outbox[0].to + mail.outbox[1].to)
            self.assertIn('mail2@example.net', mail.outbox[0].to + mail.outbox[1].to)
            a1 = Application.objects.get(email=mail.outbox[0].to[0])
            self.assertIn('{0}/en/studygroup/{1}/survey/?learner={2}'.format(settings.DOMAIN, sg.uuid, a1.uuid), mail.outbox[0].body)

        mail.outbox = []
        # way too late
        with freeze_time("2010-02-13 19:00:00"):
            send_learner_surveys(sg)
            self.assertEqual(len(mail.outbox), 0)


    def test_facilitator_survey_email(self):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = datetime.date(2010, 1, 1)
        sg.meeting_time = datetime.time(18, 0)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)

        last_meeting = sg.meeting_set.active().order_by('meeting_date', 'meeting_time').last()
        self.assertEqual(last_meeting.meeting_date, datetime.date(2010, 2, 5))
        self.assertEqual(last_meeting.meeting_time, datetime.time(18, 0))
        self.assertEqual(sg.meeting_set.active().count(), 6)
        self.assertEqual(Reminder.objects.all().count(), 0)

        # send time is 1 hour before the last meeting
        with freeze_time("2010-02-05 16:30"):
            send_facilitator_survey(sg)
            self.assertEqual(len(mail.outbox), 0)

        with freeze_time("2010-02-05 18:34"):
            send_facilitator_survey(sg)
            self.assertEqual(len(mail.outbox), 0)

        with freeze_time("2010-02-05 17:34"):
            send_facilitator_survey(sg)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('{0}/en/studygroup/{1}/facilitator_survey/'.format(settings.DOMAIN, sg.id), mail.outbox[0].body)
            self.assertIn(sg.facilitator.email, mail.outbox[0].to)


    def test_send_facilitator_learner_survey_prompt(self):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = datetime.date(2010, 1, 1)
        sg.meeting_time = datetime.time(18,15)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)

        last_meeting = sg.meeting_set.active().order_by('meeting_date', 'meeting_time').last()
        self.assertEqual(last_meeting.meeting_date, datetime.date(2010, 2, 5))
        self.assertEqual(last_meeting.meeting_time, datetime.time(18,15))
        self.assertEqual(sg.meeting_set.active().count(), 6)
        self.assertEqual(Reminder.objects.all().count(), 0)

        with freeze_time("2010-02-06 18:30:00"):
            send_facilitator_learner_survey_prompt(sg)
            self.assertEqual(len(mail.outbox), 0)

        with freeze_time("2010-02-07 17:30:00"):
            send_facilitator_learner_survey_prompt(sg)
            self.assertEqual(len(mail.outbox), 0)

        with freeze_time("2010-02-07 19:30:00"):
            send_facilitator_learner_survey_prompt(sg)
            self.assertEqual(len(mail.outbox), 0)

        with freeze_time("2010-02-07 18:30:00"):
            send_facilitator_learner_survey_prompt(sg)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('{0}/en/studygroup/{1}/facilitator_survey/'.format(settings.DOMAIN, sg.id), mail.outbox[0].body)
            self.assertIn(sg.facilitator.email, mail.outbox[0].to)


    @patch('studygroups.charts.LearnerGoalsChart.generate', mock_generate)
    @patch('studygroups.charts.GoalsMetChart.generate', mock_generate)
    def test_send_final_learning_circle_report_email(self):
        organizer = User.objects.create_user('organ@team.com', 'organ@team.com', 'password')
        facilitator = User.objects.create_user('faci1@team.com', 'faci1@team.com', 'password')
        StudyGroup.objects.filter(pk=1).update(facilitator=facilitator)

        team = Team.objects.create(name='test team')
        TeamMembership.objects.create(team=team, user=organizer, role=TeamMembership.ORGANIZER)
        TeamMembership.objects.create(team=team, user=facilitator, role=TeamMembership.MEMBER)

        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = datetime.date(2010, 1, 1)
        sg.meeting_time = datetime.time(18,0)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)

        data = dict(self.APPLICATION_DATA)
        data['study_group'] = sg
        data['email'] = 'mail1@example.net'
        application = Application(**data)
        application.save()
        accept_application(application)

        mail.outbox = []

        last_meeting = sg.meeting_set.active().order_by('meeting_date', 'meeting_time').last()
        self.assertEqual(last_meeting.meeting_date, datetime.date(2010, 2, 5))
        self.assertEqual(last_meeting.meeting_time, datetime.time(18,0))
        self.assertEqual(sg.meeting_set.active().count(), 6)
        self.assertEqual(Reminder.objects.all().count(), 0)

        # send time is 7 days after the last meeting
        with freeze_time("2010-02-12 17:30:00"):
            send_final_learning_circle_report(sg)
            self.assertEqual(len(mail.outbox), 0)

        # freeze time to 2 hours after send time
        with freeze_time("2010-02-12 19:30:00"):
            send_final_learning_circle_report(sg)
            self.assertEqual(len(mail.outbox), 0)

        # freeze time to 30 minutes after send time
        with freeze_time("2010-02-12 18:30:00"):
            send_final_learning_circle_report(sg)
            self.assertIn(application.email, mail.outbox[0].bcc)
            self.assertIn(facilitator.email, mail.outbox[0].bcc)
            self.assertIn(organizer.email, mail.outbox[0].bcc)
            self.assertEqual(len(mail.outbox[0].bcc), 3)
            self.assertIn('{0}/en/studygroup/{1}/report/'.format(settings.DOMAIN, sg.id), mail.outbox[0].body)


    def test_generate_last_week_activity_email(self):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = "UTC"
        sg.meeting_time = datetime.time(18, 0)
        sg.end_date = datetime.date(2018, 1, 6)
        sg.start_date = sg.end_date - datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)

        # freeze time to 3 days before last meeting
        with freeze_time("2018-01-03 17:59:00"):
            send_last_week_group_activity(sg)
            self.assertEqual(len(mail.outbox), 0)

        # freeze time to less than 2 days before last meeting
        with freeze_time("2018-01-04 18:01:00"):
            send_last_week_group_activity(sg)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn(sg.facilitator.email, mail.outbox[0].to)

        mail.outbox = []
        # freeze time to less than 1 day before last meeting
        with freeze_time("2018-01-05 18:01:00"):
            send_last_week_group_activity(sg)
            self.assertEqual(len(mail.outbox), 0)


    @patch('studygroups.charts.LearningCircleMeetingsChart.generate', mock_generate)
    @patch('studygroups.charts.LearningCircleCountriesChart.generate', mock_generate)
    @patch('studygroups.charts.NewLearnerGoalsChart.generate', mock_generate)
    @patch('studygroups.charts.TopTopicsChart.generate', mock_generate)
    def test_send_community_digest_email(self):
        with freeze_time("2018-01-15 11:00:00"):
            send_out_community_digest()

            today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = today
            start_date = end_date - datetime.timedelta(days=21)

            web_version_path = reverse('studygroups_community_digest', kwargs={'start_date': start_date.strftime("%d-%m-%Y"), 'end_date': end_date.strftime("%d-%m-%Y")})
            web_version_url = "{}://{}".format(settings.PROTOCOL, settings.DOMAIN) + web_version_path

            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to[0], settings.COMMUNITY_DIGEST_EMAIL)
            self.assertEqual(mail.outbox[0].subject, "P2PU Community Digest for {} to {}".format(start_date.strftime("%b %-d"), end_date.strftime("%b %-d")))
            self.assertIn("Community Digest", mail.outbox[0].body)
            self.assertIn(web_version_url, mail.outbox[0].body)


    def test_do_not_send_community_digest_email(self):
        with freeze_time("2018-01-08 11:00:00"):
            send_out_community_digest()

            self.assertEqual(len(mail.outbox), 0)


