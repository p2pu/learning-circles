from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import get_language

from mock import patch
from freezegun import freeze_time

from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import Rsvp
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import accept_application
from studygroups.models import generate_reminder
from studygroups.models import send_reminder
from studygroups.models import create_rsvp
from studygroups.models import generate_all_meetings
from studygroups.models import send_weekly_update
from studygroups.models import send_survey_reminder
from studygroups.models import send_facilitator_survey
from studygroups.models import send_last_week_group_activity
from studygroups.rsvp import gen_rsvp_querystring
from studygroups.rsvp import check_rsvp_signature
from studygroups.utils import gen_unsubscribe_querystring
from studygroups.utils import check_unsubscribe_signature

from studygroups import tasks

import calendar
import datetime
import pytz
import re
import urllib.parse
import urllib.request, urllib.parse, urllib.error
import json

# Create your tests here.
class TestSignupModels(TestCase):

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
        user.is_staff = True
        user.save()


    def test_accept_application(self):
        # TODO remove this test
        self.assertEqual(Application.objects.active().count(), 0)
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.get(pk=1)
        application = Application(**data)
        application.save()
        accept_application(application)
        self.assertEqual(Application.objects.active().count(), 1)


    def test_get_all_meeting_datetimes(self):
        # TODO
        return
        # setup test accross daylight savings time
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = 'US/Central'
        sg.meeting_time = datetime.time(16, 0)
        tz = pytz.timezone(sg.timezone)

        for i in range(56):
            start_date = datetime.date(2015, 1, 1) + datetime.timedelta(weeks=i)
            end_date = start_date + datetime.timedelta(weeks=5)
            sg.start_date = start_date
            sg.end_date = end_date
            meeting_times = get_all_meeting_times(sg)
            self.assertEqual(len(meeting_times), 6)
            self.assertEqual(meeting_times[0].date(), sg.start_date)
            self.assertEqual(meeting_times[-1].date(), sg.end_date)
            for meeting_time in meeting_times:
                self.assertEqual(datetime.time(16,0), meeting_time.time())


    def test_generate_all_meetings(self):
        now = timezone.now()
        self.assertEqual(Reminder.objects.all().count(), 0)
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = 'US/Central'
        sg.start_date = now.date() + datetime.timedelta(days=3)
        sg.meeting_time = datetime.time(16,0)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        self.assertEqual(Meeting.objects.all().count(),0)
        generate_all_meetings(sg)
        self.assertEqual(Meeting.objects.all().count(),6)
        self.assertEqual(sg.next_meeting().meeting_datetime().tzinfo.zone, 'US/Central')
        for meeting in Meeting.objects.all():
            self.assertEqual(meeting.meeting_datetime().time(), datetime.time(16,0))


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


    @patch('studygroups.models.send_message')
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
        self.assertIn('https://example.net/{0}/rsvp/?user=test%40mail.com&study_group=1&meeting_date={1}&attending=yes&sig='.format(get_language(), urllib.parse.quote(sg.next_meeting().meeting_datetime().isoformat())), mail.outbox[1].body)
        self.assertIn('https://example.net/{0}/rsvp/?user=test%40mail.com&study_group=1&meeting_date={1}&attending=no&sig='.format(get_language(), urllib.parse.quote(sg.next_meeting().meeting_datetime().isoformat())), mail.outbox[1].body)
        self.assertIn('https://example.net/{0}/optout/confirm/?user='.format(get_language()), mail.outbox[1].body)


    @patch('studygroups.models.send_message')
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
        self.assertNotIn('https://example.net/{0}/rsvp/'.format(get_language()), mail.outbox[1].body)
        self.assertIn('https://example.net/{0}/facilitator/'.format(get_language()), mail.outbox[1].body)
        self.assertNotIn('https://example.net/{0}/optout/confirm/?user='.format(get_language()), mail.outbox[1].body)


    @patch('studygroups.models.send_message')
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
            tasks.send_reminders()
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
            tasks.send_reminders()
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Reminder.objects.filter(sent_at__isnull=True).count(), 1)



    @patch('studygroups.models.send_message')
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


    @patch('studygroups.models.send_message')
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


    def test_unapply_signing(self):
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.all().first()
        application = Application(**data)
        application.save()
        qs = application.unapply_link()
        qs = qs[qs.index('?')+1:]
        sig = urllib.parse.parse_qs(qs).get('sig')[0]
        self.assertTrue(check_unsubscribe_signature(application.pk, sig))
        self.assertFalse(check_unsubscribe_signature(application.pk+1, sig))


    def test_rsvp_signing(self):
        meeting_date = timezone.datetime(2015,9,17,17,0, tzinfo=timezone.utc)
        qs = gen_rsvp_querystring('test@mail.com', '1', meeting_date, 'yes')
        sig = urllib.parse.parse_qs(qs).get('sig')[0]
        self.assertTrue(check_rsvp_signature('test@mail.com', '1', meeting_date, 'yes', sig))
        self.assertFalse(check_rsvp_signature('tes@mail.com', '1', meeting_date, 'yes', sig))
        self.assertFalse(check_rsvp_signature('test@mail.com', '2', meeting_date, 'yes', sig))
        self.assertFalse(check_rsvp_signature('test@mail.com', '1', meeting_date, 'no', sig))
        meeting_date = timezone.datetime(2015,9,18,17,0, tzinfo=timezone.utc)
        self.assertFalse(check_rsvp_signature('test@mail.com', '1', meeting_date, 'yes', sig))


    def test_create_rsvp(self):
        data = self.APPLICATION_DATA
        data['study_group'] = StudyGroup.objects.get(pk=1)
        application = Application(**data)
        application.save()
        sg = StudyGroup.objects.get(pk=1)
        meeting_date = timezone.now()
        sgm = Meeting(
            study_group=sg,
            meeting_time=meeting_date.time(),
            meeting_date=meeting_date.date()
        )
        sgm.save()
        sgm = Meeting(
            study_group=sg,
            meeting_time=meeting_date.time(),
            meeting_date=meeting_date.date() + datetime.timedelta(weeks=1)
        )
        sgm.save()


        # Test creating an RSVP
        self.assertEqual(Rsvp.objects.all().count(), 0)
        create_rsvp('test@mail.com', sg.id, meeting_date, 'yes')
        self.assertEqual(Rsvp.objects.all().count(), 1)
        self.assertTrue(Rsvp.objects.all().first().attending)

        # Test updating an RSVP
        create_rsvp('test@mail.com', sg.id, meeting_date, 'no')
        self.assertEqual(Rsvp.objects.all().count(), 1)
        self.assertFalse(Rsvp.objects.all().first().attending)


    def test_send_new_facilitator_update(self):
        tasks.send_new_facilitator_emails()
        self.assertEqual(len(mail.outbox), 0)

        user = User.objects.create_user('facil', 'facil@test.com', 'password')
        user.date_joined = timezone.now() - datetime.timedelta(days=7)
        user.save()
        tasks.send_new_facilitator_emails()
        self.assertEqual(len(mail.outbox), 1)


    def test_send_new_studygroup_update(self):
        tasks.send_new_studygroup_emails()
        self.assertEqual(len(mail.outbox), 0)

        studygroup = StudyGroup.objects.get(pk=1)
        studygroup.created_at = timezone.now() - datetime.timedelta(days=7)
        studygroup.save()


        tasks.send_new_studygroup_emails()
        self.assertEqual(len(mail.outbox), 1)


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
        meeting.meeting_time = timezone.now().time()
        meeting.meeting_date = timezone.now().date() - datetime.timedelta(days=1)
        meeting.save()

        study_group = StudyGroup.objects.get(pk=2)
        meeting = Meeting()
        meeting.study_group = study_group
        meeting.meeting_time = timezone.now().time()
        meeting.meeting_date = timezone.now().date() - datetime.timedelta(days=1)
        meeting.save()

        send_weekly_update()

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to[0], 'organ@team.com')
        self.assertEqual(mail.outbox[1].to[0], 'admin@test.com')


    def test_send_survey_reminder(self):
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

        data = dict(self.APPLICATION_DATA)
        data['study_group'] = sg
        data['email'] = 'mail2@example.net'
        application = Application(**data)
        accept_application(application)
        application.save()

        mail.outbox = []

        last_meeting = sg.meeting_set.active().order_by('meeting_date', 'meeting_time').last()
        self.assertEqual(last_meeting.meeting_date, datetime.date(2010, 2, 5))
        self.assertEqual(last_meeting.meeting_time, datetime.time(18,0))
        self.assertEqual(sg.meeting_set.active().count(), 6)
        self.assertEqual(sg.application_set.active().count(), 2)

        # freeze time to 5 minutes before
        with freeze_time("2010-02-05 17:55:34"):
            send_survey_reminder(sg)
            self.assertEqual(len(mail.outbox), 0)

        # 10 minutes after start
        with freeze_time("2010-02-05 18:10:34"):
            send_survey_reminder(sg)
            self.assertEqual(len(mail.outbox), 0)

        # 25 minutes after start
        with freeze_time("2010-02-05 18:25:34"):
            send_survey_reminder(sg)
            self.assertEqual(len(mail.outbox), 2)
            self.assertIn('mail1@example.net', mail.outbox[0].to + mail.outbox[1].to)
            self.assertIn('mail2@example.net', mail.outbox[0].to + mail.outbox[1].to)
            a1 = Application.objects.get(email=mail.outbox[0].to[0])
            self.assertIn('https://example.net/en/studygroup/{}/feedback/?learner={}'.format(sg.uuid, a1.uuid), mail.outbox[0].body)

        mail.outbox = []
        # 40 minutes after start
        with freeze_time("2010-02-05 18:40:34"):
            send_survey_reminder(sg)
            self.assertEqual(len(mail.outbox), 0)


    def test_generate_final_reminder(self):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = datetime.date(2010, 1, 1)
        sg.meeting_time = datetime.time(18,0)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)

        last_meeting = sg.meeting_set.active().order_by('meeting_date', 'meeting_time').last()
        self.assertEqual(last_meeting.meeting_date, datetime.date(2010, 2, 5))
        self.assertEqual(last_meeting.meeting_time, datetime.time(18,0))
        self.assertEqual(sg.meeting_set.active().count(), 6)
        self.assertEqual(Reminder.objects.all().count(), 0)

        # freeze time to 2 days before last meeting
        with freeze_time("2010-02-03 17:55:34"):
            send_survey_reminder(sg)
            self.assertEqual(len(mail.outbox), 0)
            generate_reminder(sg)
            self.assertEqual(Reminder.objects.all().count(), 1)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('/static/uploads/learner_survey.pdf', mail.outbox[0].body)

    def test_generate_finished_studygroup_feedback_email(self):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.start_date = datetime.date(2010, 1, 1)
        sg.meeting_time = datetime.time(18,0)
        sg.end_date = sg.start_date + datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)

        last_meeting = sg.meeting_set.active().order_by('meeting_date', 'meeting_time').last()
        self.assertEqual(last_meeting.meeting_date, datetime.date(2010, 2, 5))
        self.assertEqual(last_meeting.meeting_time, datetime.time(18,0))
        self.assertEqual(sg.meeting_set.active().count(), 6)
        self.assertEqual(Reminder.objects.all().count(), 0)

        # freeze time to 6 days after last
        with freeze_time("2010-02-11 17:55:34"):
            send_facilitator_survey(sg)
            self.assertEqual(len(mail.outbox), 0)

        # freeze time to 8 days after last
        with freeze_time("2010-02-13 17:55:34"):
            send_facilitator_survey(sg)
            self.assertEqual(len(mail.outbox), 0)

        # freeze time to 7 days after last
        with freeze_time("2010-02-12 17:55:34"):
            send_facilitator_survey(sg)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn('https://example.net/en/studygroup/{0}/facilitator_feedback/'.format(sg.uuid), mail.outbox[0].body)
            self.assertIn(sg.facilitator.email, mail.outbox[0].to)


    def test_generate_last_week_activity_email(self):
        now = timezone.now()
        sg = StudyGroup.objects.get(pk=1)
        sg.timezone = now.strftime("%Z")
        sg.meeting_time = datetime.time(18,0)
        sg.end_date = datetime.date(2018, 1, 6)
        sg.start_date = sg.end_date - datetime.timedelta(weeks=5)
        sg.save()
        sg = StudyGroup.objects.get(pk=1)
        generate_all_meetings(sg)

        # freeze time to more than 2 days before last meeting
        with freeze_time("2018-01-03 00:00:00"):
            send_last_week_group_activity(sg)
            self.assertEqual(len(mail.outbox), 0)

        # freeze time to less than 2 days before last meeting
        with freeze_time("2018-01-05 00:00:00"):
            send_last_week_group_activity(sg)
            self.assertEqual(len(mail.outbox), 1)
            self.assertIn(sg.facilitator.email, mail.outbox[0].to)
