from django.db import models
from django.db.models.signals import post_init
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse #TODO ideally this shouldn't be in the model

from s3direct.fields import S3DirectField

from studygroups.sms import send_message
from studygroups import rsvp

import calendar
import datetime
import pytz
import dateutil.parser
import re

STUDY_GROUP_NAMES = [
    "The Riders",
    "The Master Minds of Mars",
    "The Efficiency Experts",
    "The Red Hawks",
    "The Bandits of Hell's Bend",
    "Apache Devils",
    "The Wizards of Venus",
    "Swords of Mars",
    "The Beasts of Tarzan",
    "Tarzan and the Castaways",
    "Pirates of Venus",
    "The People that Time Forgot",
    "The Eternal Lovers"
]


def _study_group_name():
    idx = 1 + StudyGroup.objects.count()
    num_names = len(STUDY_GROUP_NAMES)
    return ' '.join([STUDY_GROUP_NAMES[idx%num_names], "I"*(idx/num_names)])


class Course(models.Model):
    title = models.CharField(max_length=128)
    provider = models.CharField(max_length=256)
    link = models.URLField()
    image = S3DirectField(dest='imgs', blank=True)
    key = models.CharField(max_length=255, default='NOT SET')
    start_date = models.DateField()
    duration = models.CharField(max_length=128)
    prerequisite = models.TextField()
    time_required = models.CharField(max_length=128)
    #TODO clarify difference between caption and description
    caption = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title


class Location(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    contact_name = models.CharField(max_length=256)
    contact = models.CharField(max_length=256)
    link = models.URLField()
    image = models.ImageField(blank=True)

    def __unicode__(self):
        return self.name


class StudyGroup(models.Model):
    name = models.CharField(max_length=128, default=_study_group_name)
    course = models.ForeignKey('studygroups.Course')
    location = models.ForeignKey('studygroups.Location')
    location_details = models.CharField(max_length=128)
    facilitator = models.ForeignKey(User)
    start_date = models.DateTimeField() # start_date also implies regular meeting day & time. Ex. Wednesday 1 July at 19:00 implies regular meetings on Wednesday at 19:00
    end_date = models.DateTimeField()
    duration = models.IntegerField() # meeting duration in minutes
    timezone = models.CharField(max_length=128)
    max_size = models.IntegerField() #TODO remove this field
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def day(self):
        return calendar.day_name[self.start_date.weekday()]

    def end_time(self):
        q = self.start_date + datetime.timedelta(minutes=self.duration)
        return q.time()

    def next_meeting(self):
        return self.studygroupmeeting_set.filter(meeting_time__gt=timezone.now()).order_by('meeting_time').first()

    def meeting_times(self):
        return get_all_meeting_times(self)

    def __unicode__(self):
        return u'{0} - {1}s {2} at the {3}'.format(self.course.title, self.day(), self.start_date.time(), self.location)


class Application(models.Model):
    EMAIL = 'Email'
    TEXT = 'Text'
    PREFERRED_CONTACT_METHOD = [
        (EMAIL, 'Email'),
        (TEXT, 'Text'),
    ]

    NO = 'No'
    SOMETIMES = 'Sometimes'
    YES = 'Yes'
    COMPUTER_ACCESS = [
        (NO, 'No'),
        (SOMETIMES, 'Sometimes'),
        (YES, 'Yes'),
    ]

    study_group = models.ForeignKey('studygroups.StudyGroup')
    name = models.CharField(max_length=128)
    contact_method = models.CharField(max_length=128, choices=PREFERRED_CONTACT_METHOD)
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    computer_access = models.CharField(max_length=128, choices=COMPUTER_ACCESS)
    goals = models.TextField()
    support = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u"{0} <{1}>".format(self.name, self.email if self.contact_method==self.EMAIL else self.mobile)


class StudyGroupMeeting(models.Model):
    study_group = models.ForeignKey('studygroups.StudyGroup')
    meeting_time = models.DateTimeField(blank=True, null=True)


class Reminder(models.Model):
    study_group = models.ForeignKey('studygroups.StudyGroup')
    study_group_meeting = models.ForeignKey('studygroups.StudyGroupMeeting', blank=True, null=True)
    email_subject = models.CharField(max_length=256)
    email_body = models.TextField()
    sms_body = models.CharField(max_length=160)

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)


class Rsvp(models.Model):
    study_group_meeting = models.ForeignKey('studygroups.StudyGroupMeeting')
    application = models.ForeignKey('studygroups.Application')
    attending = models.BooleanField()

    def __unicode__(self):
        return u'{0} ({1})'.format(self.application, 'yes' if self.attending else 'no')


class Feedback(models.Model):
    study_group_meeting = models.ForeignKey('studygroups.StudyGroupMeeting')
    feedback = models.CharField(max_length=255)


def accept_application(application):
    # add a study group application to a study group
    application.accepted_at = timezone.now()
    application.save()


def get_all_meeting_times(study_group):
    # sorted ascending according to date
    # times are in the study group timezone
    # meeting time stays constant, eg 18:00 stays 18:00 even when daylight savings changes
    tz = pytz.timezone(study_group.timezone)
    next_meeting = tz.normalize(study_group.start_date)
    meetings = []
    while next_meeting <= study_group.end_date:
        meetings += [next_meeting]
        next_meeting += datetime.timedelta(days=7)
        # Next two steps are to keep meetings at the same time even when daylight savings kick in or end 
        next_meeting = datetime.datetime.combine(next_meeting, next_meeting.time()) 
        next_meeting = tz.localize(next_meeting)
    return meetings


def next_meeting_date(study_group):
    meetings = get_all_meeting_times(study_group)
    return next((meeting for meeting in meetings if meeting > timezone.now()), [None])


def generate_all_meetings(study_group):
    if StudyGroupMeeting.objects.filter(study_group=study_group).exists():
        raise Exception('Meetings already exist for this study group')
    meeting_times = get_all_meeting_times(study_group)
    for meeting_time in meeting_times:
        meeting = StudyGroupMeeting(study_group=study_group, meeting_time=meeting_time)
        meeting.save()


def generate_reminder(study_group):
    now = timezone.now()
    next_meeting = study_group.next_meeting()
    if next_meeting and next_meeting.meeting_time - now < datetime.timedelta(days=3):
        # check if a notifcation already exists for this meeting
        if not Reminder.objects.filter(study_group=study_group, study_group_meeting=next_meeting).exists():
            reminder = Reminder()
            reminder.study_group = study_group
            reminder.study_group_meeting = next_meeting
            context = { 
                'study_group': study_group,
                'next_meeting': next_meeting,
                'reminder': reminder
            }
            timezone.activate(pytz.timezone(study_group.timezone))
            reminder.email_subject = render_to_string(
                'studygroups/notifications/reminder-subject.txt',
                context
            )
            reminder.email_body = render_to_string(
                'studygroups/notifications/reminder.html',
                context
            )
            reminder.sms_body = render_to_string(
                'studygroups/notifications/sms.txt',
                context
            )
            reminder.save()
            
            facilitator_notification_subject = u'A reminder for {0} was generated'.format(study_group.course.title)
            facilitator_notification = render_to_string(
                'studygroups/notifications/reminder-notification.html',
                context
            )
            timezone.deactivate()
            to = [study_group.facilitator.email]
            send_mail(
                facilitator_notification_subject,
                facilitator_notification,
                settings.SERVER_EMAIL,
                to,
                fail_silently=False
            )


def send_reminder(reminder):
    to = [su.email for su in reminder.study_group.application_set.filter(accepted_at__isnull=False, contact_method=Application.EMAIL)]
    if reminder.study_group_meeting:
        # this is a reminder and we need RSVP links
        for email in to:
            # TODO hardcoded domain
            domain = 'https://chicago.p2pu.org'
            url = reverse('studygroups_rsvp')
            yes_qs = rsvp.gen_rsvp_querystring(
                email,
                reminder.study_group.pk,
                reminder.study_group_meeting.meeting_time,
                'yes'
            )
            yes_link = '{0}{1}?{2}'.format(domain,url,yes_qs)
            no_qs = rsvp.gen_rsvp_querystring(
                email,
                reminder.study_group.pk,
                reminder.study_group_meeting.meeting_time,
                'no'
            )
            no_link = '{0}{1}?{2}'.format(domain,url,no_qs)
            email_body = reminder.email_body
            email_body = re.sub(r'<!--RSVP:YES.*-->', yes_link, email_body)
            email_body = re.sub(r'<!--RSVP:NO.*-->', no_link, email_body)
            send_mail(
                    reminder.email_subject.strip('\n'),
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False
            )
    else:
        send_mail(reminder.email_subject.strip('\n'), reminder.email_body, settings.DEFAULT_FROM_EMAIL, to, fail_silently=False)

    # send SMS
    tos = [su.mobile for su in reminder.study_group.application_set.filter(accepted_at__isnull=False, contact_method=Application.TEXT)]
    errors = []
    for to in tos:
        if reminder.study_group_meeting:
            #TODO - insert RSVP link
            send_message(to, reminder.sms_body)
        try:
            send_message(to, reminder.sms_body)
        except twilio.TwilioRestException as e:
            errors.push[e]
    if len(errors):
        #TODO: log errors
        raise Exception(errors)

    reminder.sent_at = timezone.now()
    reminder.save()


def create_rsvp(contact, study_group, meeting_date, attending):
    # expect meeting_date in isoformat
    # contact is an email address of mobile number
    # study_group is the study group id
    meeting_date = dateutil.parser.parse(meeting_date)
    study_group_meeting = StudyGroupMeeting.objects.get(study_group__id=study_group, meeting_time=meeting_date)
    application = None
    if '@' in contact:
        application = Application.objects.get(study_group__id=study_group, email=contact)
    else:
        application = Application.objects.get(study_group__id=study_group, mobile=contact)
    rsvp = Rsvp.objects.all().filter(study_group_meeting=study_group_meeting, application=application).first()
    if not rsvp:
        rsvp = Rsvp(study_group_meeting=study_group_meeting, application=application, attending=attending=='yes')
    else:
        rsvp.attending=attending=='yes'
    rsvp.save()
    return rsvp
