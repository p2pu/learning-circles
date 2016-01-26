from django.db import models
from django.db.models.signals import post_init
from django.utils import timezone
from django.utils import translation
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse #TODO ideally this shouldn't be in the model

import twilio

from studygroups.sms import send_message
from studygroups import rsvp

import calendar
import datetime
import pytz
import dateutil.parser
import re
import logging

logger = logging.getLogger(__name__)

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


class SoftDeleteQuerySet(models.QuerySet):

    def active(self):
        return self.filter(deleted_at__isnull=True)

    def delete(self, *args, **kwargs):
        # Stop bulk deletes
        self.update(deleted_at=timezone.now())
        #TODO: check if we need to set any flags on the query set after the delete


class LifeTimeTrackingModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        # Don't actually delete the object, affects django admin also
        self.deleted_at = timezone.now()
        self.save()
        
    class Meta:
        abstract = True


class Course(models.Model):
    title = models.CharField(max_length=128)
    provider = models.CharField(max_length=256)
    link = models.URLField(help_text='URL where the course can be accessed.')
    key = models.CharField(max_length=255, default='NOT SET')
    start_date = models.DateField()
    duration = models.IntegerField(help_text='Number of weeks.')
    prerequisite = models.TextField(blank=True)
    time_required = models.IntegerField(help_text='Number of hours per week.')
    caption = models.TextField(help_text='Short description of the course.')
    created_by = models.ForeignKey(User, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title


class Location(models.Model):
    name = models.CharField(max_length=256, help_text='Common name used to refer to the location.')
    address = models.CharField(max_length=256, help_text='Street address of the location.')
    contact_name = models.CharField(max_length=256, help_text='Person that can be contacted at the location.')
    contact = models.CharField(max_length=256, help_text='Email or phone for the contact person.')
    link = models.URLField(blank=True, help_text='URL where more info about the location can be seen.')
    image = models.ImageField(blank=True, help_text='A photo to represent your Learning Circle. It could be a picture of the building, or anything else you\'d like to choose!')

    def __unicode__(self):
        return self.name


class Activity(models.Model):
    description = models.CharField(max_length=256)
    index = models.PositiveIntegerField(help_text='meeting index this activity corresponds to')
    card = models.FileField()

    def __unicode__(self):
        return self.description


class Facilitator(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return self.user.__unicode__()


class Organizer(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return self.user.__unicode__()


class StudyGroup(LifeTimeTrackingModel):
    name = models.CharField(max_length=128, default=_study_group_name)
    course = models.ForeignKey('studygroups.Course', help_text='Choose one or add a new course.')
    location = models.ForeignKey('studygroups.Location') # TODO - remove this
    venue_name = models.CharField(max_length=256, verbose_name='Common name of venue.', help_text='e.g. Pretoria Library or Bekka\'s house')
    venue_address = models.CharField(max_length=256, help_text='Like you were mailing a letter. Include country!.')
    venue_details = models.CharField(max_length=128, verbose_name='Meeting spot', help_text='e.g. second floor meeting room or kitchen.')
    venue_website = models.URLField(blank=True, help_text='Link to any website that has more info about the venue or Circle.')
    location_details = models.CharField(max_length=128, help_text='Meeting room or office number.') # TODO - remove this field
    facilitator = models.ForeignKey(User)
    start_date = models.DateField(verbose_name='First meeting date', help_text='Give yourself at least 4 weeks to market, if possible.')
    meeting_time = models.TimeField()
    end_date = models.DateField() # TODO consider storing number of weeks/meetings instead of end_date
    duration = models.IntegerField(verbose_name='Length of each Circle', help_text='We recommend 90 minutes - 2 hours.', default=90) # meeting duration in minutes
    timezone = models.CharField(max_length=128)
    signup_open = models.BooleanField(default=True)
    image = models.ImageField(blank=True, help_text='Make your Circle stand out with a picture. It could be related to location, subject matter, or anything else you want to identify your Circle with.')

    def day(self):
        return calendar.day_name[self.start_date.weekday()]

    def end_time(self):
        q = datetime.datetime.combine(self.start_date, self.meeting_time) + datetime.timedelta(minutes=self.duration)
        return q.time()

    def next_meeting(self):
        return self.studygroupmeeting_set.filter(meeting_time__gt=timezone.now()).order_by('meeting_time').first()

    def meeting_times(self):
        return get_all_meeting_times(self)

    def local_start_date(self):
        tz = pytz.timezone(self.timezone)
        date = datetime.datetime.combine(self.start_date, self.meeting_time)
        return tz.localize(date)

    def timezone_display(self):
        return self.local_start_date().strftime("%Z")

    def __unicode__(self):
        return u'{0} - {1}s {2} at the {3}'.format(self.course.title, self.day(), self.meeting_time, self.location)


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
    meeting_time = models.DateTimeField()

    def meeting_number(self):
        return StudyGroupMeeting.objects.filter(meeting_time__lte=self.meeting_time, study_group=self.study_group).count()

    def meeting_activity(self):
        return next((a for a in Activity.objects.filter(index=self.meeting_number)), None)

    def rsvps(self):
        return {
            'yes': self.rsvp_set.all().filter(attending=True),
            'no': self.rsvp_set.all().filter(attending=False)
        }

    def rsvp_yes_link(self, email):
        domain = 'https://{0}'.format(settings.DOMAIN)
        url = reverse('studygroups_rsvp')
        yes_qs = rsvp.gen_rsvp_querystring(
            email,
            self.study_group.pk,
            self.meeting_time,
            'yes'
        )
        return '{0}{1}?{2}'.format(domain,url,yes_qs)

    def rsvp_no_link(self, email):
        domain = 'https://{0}'.format(settings.DOMAIN)
        url = reverse('studygroups_rsvp')
        no_qs = rsvp.gen_rsvp_querystring(
            email,
            self.study_group.pk,
            self.meeting_time,
            'no'
        )
        return '{0}{1}?{2}'.format(domain,url,no_qs)

    def __unicode__(self):
        tz = pytz.timezone(self.study_group.timezone)
        return u'{0}, {1} at {2}'.format(self.study_group.course.title, tz.normalize(self.meeting_time), self.study_group.location.name)


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

    BAD = '1'
    NOT_SO_GOOD = '2'
    GOOD = '3'
    WELL = '4'
    GREAT = '5'

    RATING = [
        (GREAT, 'Great'),
        (WELL, 'Pretty well'),
        (GOOD, 'Good'),
        (NOT_SO_GOOD, 'Not so great'),
        (BAD, 'I need some help'),
    ]

    study_group_meeting = models.ForeignKey('studygroups.StudyGroupMeeting')
    feedback = models.TextField() # Shared with learners
    attendance = models.PositiveIntegerField()
    reflection = models.TextField() # Not shared
    rating = models.CharField(choices=RATING, max_length=16)


def accept_application(application):
    # add a study group application to a study group
    application.accepted_at = timezone.now()
    application.save()


def get_all_meeting_times(study_group):
    # sorted ascending according to date
    # times are in the study group timezone
    # meeting time stays constant, eg 18:00 stays 18:00 even when daylight savings changes
    tz = pytz.timezone(study_group.timezone)
    meeting_date = study_group.start_date
    meetings = []
    while meeting_date <= study_group.end_date:
        next_meeting = tz.localize(datetime.datetime.combine(meeting_date, study_group.meeting_time))
        meetings += [next_meeting]
        meeting_date += datetime.timedelta(days=7)
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


# If called directly, be sure to activate the current language
def generate_reminder(study_group):
    now = timezone.now()
    next_meeting = study_group.next_meeting()
    if next_meeting and next_meeting.meeting_time - now < datetime.timedelta(days=4):
        # check if a notifcation already exists for this meeting
        if not Reminder.objects.filter(study_group=study_group, study_group_meeting=next_meeting).exists():
            reminder = Reminder()
            reminder.study_group = study_group
            reminder.study_group_meeting = next_meeting
            context = { 
                'study_group': study_group,
                'next_meeting': next_meeting,
                'reminder': reminder,
                'protocol': 'https',
                'domain': settings.DOMAIN,
            }
            previous_meeting = study_group.studygroupmeeting_set.filter(meeting_time__lt=next_meeting.meeting_time).order_by('meeting_time').last()
            if previous_meeting and previous_meeting.feedback_set.first():
                context['feedback'] = previous_meeting.feedback_set.first()
            timezone.activate(pytz.timezone(study_group.timezone))
            #TODO do I need to activate a locale?
            reminder.email_subject = render_to_string(
                'studygroups/notifications/reminder-subject.txt',
                context
            )
            reminder.email_body = render_to_string(
                'studygroups/notifications/reminder.txt',
                context
            )
            reminder.sms_body = render_to_string(
                'studygroups/notifications/sms.txt',
                context
            )
            reminder.save()

            facilitator_notification_subject = u'A reminder for {0} was generated'.format(study_group.course.title)
            facilitator_notification_html = render_to_string(
                'studygroups/notifications/reminder-notification.html',
                context
            )
            facilitator_notification_txt = render_to_string(
                'studygroups/notifications/reminder-notification.txt',
                context
            )
            timezone.deactivate()
            to = [study_group.facilitator.email]
            bcc = [ admin[1] for admin in settings.ADMINS ]
            notification = EmailMultiAlternatives(
                facilitator_notification_subject,
                facilitator_notification_txt,
                settings.SERVER_EMAIL,
                to,
                bcc
            )
            notification.attach_alternative(facilitator_notification_html, 'text/html')
            notification.send()


# If called directly, be sure to active language to use for constructing URLs
# Failed text delivery won't case this function to fail, simply log an error
def send_reminder(reminder):
    to = [su.email for su in reminder.study_group.application_set.filter(accepted_at__isnull=False, contact_method=Application.EMAIL)]
    if reminder.study_group_meeting:
        # this is a reminder and we need RSVP links
        for email in to:
            yes_link = reminder.study_group_meeting.rsvp_yes_link(email)
            no_link = reminder.study_group_meeting.rsvp_no_link(email)
            email_body = reminder.email_body
            email_body = re.sub(r'\(<!--RSVP:YES-->.*\)', yes_link, email_body)
            email_body = re.sub(r'\(<!--RSVP:NO-->.*\)', no_link, email_body)
            send_mail(
                reminder.email_subject.strip('\n'),
                email_body,
                reminder.study_group.facilitator.email,
                [email],
                fail_silently=False
            )
    else:
        send_mail(reminder.email_subject.strip('\n'), reminder.email_body, reminder.study_group.facilitator.email, to, fail_silently=False)

    # send SMS
    tos = [su.mobile for su in reminder.study_group.application_set.filter(accepted_at__isnull=False, contact_method=Application.TEXT)]
    for to in tos:
        try:
            #TODO - insert RSVP link
            #if reminder.study_group_meeting:
            send_message(to, reminder.sms_body)
        except twilio.TwilioRestException as e:
            logger.exception(u"Could not send text message to %s", to, exc_info=e)

    reminder.sent_at = timezone.now()
    reminder.save()


def create_rsvp(contact, study_group, meeting_date, attending):
    # expect meeting_date as python datetime
    # contact is an email address of mobile number
    # study_group is the study group id
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
        rsvp.attending = attending=='yes'
    rsvp.save()
    return rsvp


def report_data(start_time, end_time):
    study_groups = StudyGroup.objects.all().order_by('start_date')
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    report = {
        'meetings': StudyGroupMeeting.objects.filter(meeting_time__gte=start_time, meeting_time__lt=end_time),
        'signups': Application.objects.filter(created_at__gte=start_time, created_at__lt=end_time),
    }
    return report


def send_weekly_update():
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = today - datetime.timedelta(days=today.weekday()+7)
    end_time = start_time + datetime.timedelta(days=7)
    context = {
        'start_time': start_time,
        'end_time': end_time,
        'protocol': 'https',
        'domain': settings.DOMAIN,
    }
    context.update(report_data(start_time, end_time))
    timezone.activate(pytz.timezone(settings.TIME_ZONE))
    translation.activate(settings.LANGUAGE_CODE)
    html_body = render_to_string('studygroups/weekly-update.html', context)
    text_body = render_to_string('studygroups/weekly-update.txt', context)
    timezone.deactivate()
    to = [o.user.email for o in Organizer.objects.all()]
 
    update = EmailMultiAlternatives(
        'Weekly Learning Circles update',
        text_body,
        settings.SERVER_EMAIL,
        to
    )
    update.attach_alternative(html_body, 'text/html')
    update.send()

