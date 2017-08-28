# coding=utf-8
from django.db import models
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse  # TODO ideally this shouldn't be in the model

from twilio import TwilioRestException

from studygroups.sms import send_message
from studygroups.email_helper import render_email_templates
from studygroups import rsvp
from studygroups.utils import gen_unsubscribe_querystring

import calendar
import datetime
import pytz
import re
import json
import urllib
import logging

logger = logging.getLogger(__name__)

# TODO - remove this
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
    return ' '.join([STUDY_GROUP_NAMES[idx % num_names], "I"*(idx/num_names)])


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


class Course(LifeTimeTrackingModel):
    title = models.CharField(max_length=128)
    provider = models.CharField(max_length=256)
    link = models.URLField()
    caption = models.CharField(max_length=200)
    on_demand = models.BooleanField()
    topics = models.CharField(max_length=500)
    language = models.CharField(max_length=6)
    created_by = models.ForeignKey(User, blank=True, null=True)
    unlisted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title


class Activity(models.Model):
    """ Activity to do during a meeting """
    description = models.CharField(max_length=256)
    index = models.PositiveIntegerField(help_text=_('meeting index this activity corresponds to'))
    card = models.FileField()

    def __unicode__(self):
        return self.description


# TODO rename to profile or something else
class Facilitator(models.Model):
    user = models.OneToOneField(User)
    mailing_list_signup = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.__unicode__()


# TODO remove organizer model - only use Facilitator model + Team Membership
class Organizer(models.Model):
    user = models.OneToOneField(User)

    def __unicode__(self):
        return self.user.__unicode__()


class Team(models.Model):
    name = models.CharField(max_length=128)
    page_slug = models.SlugField(max_length=256, blank=True)
    page_image = models.ImageField(blank=True)

    def __unicode__(self):
        return self.name


class TeamMembership(models.Model):
    ORGANIZER = 'ORGANIZER'
    MEMBER = 'MEMBER'
    ROLES = (
        (ORGANIZER, _('Organizer')),
        (MEMBER, _('Member')),
    )
    team = models.ForeignKey('studygroups.Team')
    user = models.OneToOneField(User) # TODO should this be a OneToOneField?
    role = models.CharField(max_length=256, choices=ROLES)

    def __unicode__(self):
        return 'Team membership: {}'.format(self.user.__unicode__())


class TeamInvitation(models.Model):
    """ invittion for users to join a team """
    team = models.ForeignKey('studygroups.Team')
    organizer = models.ForeignKey(User) # organizer who invited the user
    email = models.EmailField()
    role = models.CharField(max_length=256, choices=TeamMembership.ROLES)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    joined = models.NullBooleanField(null=True)

    def __unicode__(self):
        return u'Invatation <{} to join {}>'.format(self.email, self.team.name)


class StudyGroup(LifeTimeTrackingModel):
    name = models.CharField(max_length=128, default=_study_group_name)
    course = models.ForeignKey('studygroups.Course')
    description = models.CharField(max_length=500)
    venue_name = models.CharField(max_length=256)
    venue_address = models.CharField(max_length=256)
    venue_details = models.CharField(max_length=128)
    venue_website = models.URLField(blank=True)
    city = models.CharField(max_length=256)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    facilitator = models.ForeignKey(User)
    start_date = models.DateField()
    meeting_time = models.TimeField()
    end_date = models.DateField() # TODO consider storing number of weeks/meetings instead of end_date
    duration = models.IntegerField(default=90) # meeting duration in minutes
    timezone = models.CharField(max_length=128)
    signup_open = models.BooleanField(default=True)
    image = models.ImageField(blank=True)

    def day(self):
        return calendar.day_name[self.start_date.weekday()]

    def end_time(self):
        q = datetime.datetime.combine(self.start_date, self.meeting_time) + datetime.timedelta(minutes=self.duration)
        return q.time()

    def next_meeting(self):
        now = timezone.now()
        meeting_list = self.studygroupmeeting_set.active().order_by('meeting_date', 'meeting_time')
        return next((m for m in meeting_list if m.meeting_datetime() > now), None)

    def local_start_date(self):
        tz = pytz.timezone(self.timezone)
        date = datetime.datetime.combine(self.start_date, self.meeting_time)
        return tz.localize(date)

    def timezone_display(self):
        return self.local_start_date().strftime("%Z")

    @property
    def country(self):
        country = self.city.split(',')[-1].strip()
        country_list = [
            'United States of America',
            'Kenya',
            'France'
        ]
        if country in country_list:
            return country
        return None

    def to_dict(self):
        sg = self  # TODO
        data = {
            "course_title": sg.course.title,
            "facilitator": sg.facilitator.first_name + " " + sg.facilitator.last_name,
            "signup_count": sg.application_set.count(),
            "venue": sg.venue_name,
            "venue_address": sg.venue_address + ", " + sg.city,
            "day": sg.day(),
            "start_date": sg.start_date,
            "meeting_time": sg.meeting_time,
            "time_zone": sg.timezone_display(),
            "end_time": sg.end_time(),
            "weeks": sg.studygroupmeeting_set.active().count(),
            "url": reverse('studygroups_view_study_group', args=(sg.id,)),
            "signup_url": reverse('studygroups_signup', args=(slugify(sg.venue_name), sg.id,)),
        }
        next_meeting = self.next_meeting()
        if next_meeting:
            data['next_meeting_date'] = next_meeting.meeting_date
        if sg.image:
            data["image_url"] = "https://learningcircles.p2pu.org" + sg.image.url
        return data

    def to_json(self):
        return json.dumps(self.to_dict(), cls=DjangoJSONEncoder)


    def __unicode__(self):
        return u'{0} - {1}s {2} at the {3}'.format(self.course.title, self.day(), self.meeting_time, self.venue_name)


class Application(LifeTimeTrackingModel):
    study_group = models.ForeignKey('studygroups.StudyGroup')
    name = models.CharField(max_length=128)
    email = models.EmailField(verbose_name='Email address', blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    signup_questions = models.TextField(default='{}')
    accepted_at = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return u"{0} <{1}>".format(self.name, self.email if self.email else self.mobile)

    def unapply_link(self):
        domain = 'https://{0}'.format(settings.DOMAIN)
        url = reverse('studygroups_leave')
        qs = gen_unsubscribe_querystring(self.pk)
        return '{0}{1}?{2}'.format(domain, url, qs)

    def get_signup_questions(self):
        return json.loads(self.signup_questions)

    DIGITAL_LITERACY_QUESTIONS = {
        'use_internet': _('How comfortable are you using the internet?'),
        'send_email': _('Send an email'),
        'delete_spam': _('Delete spam email'),
        'search_online': _('Find stuff online using Google'),
        'browse_video': _('Watch a video on Youtube'),
        'online_shopping': _('Fill out an application form or buy something online'),
        'mobile_apps': _('Use a mobile app'),
        'web_safety': _('Evaluate whether a website is safe/can be trusted')
    }

    DIGITAL_LITERACY_CHOICES = (
        ('0', _(u'Can\'t do')), 
        ('1', _(u'Need help doing')),
        ('2', _(u'Can do with difficulty')), 
        ('3', _(u'Can do')),
        ('4', _(u'Expert (can teach others)')),
    )

    def digital_literacy_for_display(self):
        answers = json.loads(self.signup_questions)
        return { q: {'question_text': text, 'answer': answers.get(q), 'answer_text': dict(self.DIGITAL_LITERACY_CHOICES).get(answers.get(q)) if q in answers else ''} for q, text in self.DIGITAL_LITERACY_QUESTIONS.iteritems() if answers.get(q) }


class StudyGroupMeeting(LifeTimeTrackingModel):
    study_group = models.ForeignKey('studygroups.StudyGroup')
    meeting_date = models.DateField()
    meeting_time = models.TimeField()

    def meeting_number(self):
        # TODO this will break for two meetings on the same day
        return StudyGroupMeeting.objects.active().filter(meeting_date__lte=self.meeting_date, study_group=self.study_group).count()

    def meeting_activity(self):
        return next((a for a in Activity.objects.filter(index=self.meeting_number())), None)

    def meeting_datetime(self):
        tz = pytz.timezone(self.study_group.timezone)
        return tz.localize(datetime.datetime.combine(self.meeting_date, self.meeting_time))

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
            self.meeting_datetime(),
            'yes'
        )
        return '{0}{1}?{2}'.format(domain, url, yes_qs)

    def rsvp_no_link(self, email):
        domain = 'https://{0}'.format(settings.DOMAIN)
        url = reverse('studygroups_rsvp')
        no_qs = rsvp.gen_rsvp_querystring(
            email,
            self.study_group.pk,
            self.meeting_datetime(),
            'no'
        )
        return '{0}{1}?{2}'.format(domain,url,no_qs)

    def __unicode__(self):
        tz = pytz.timezone(self.study_group.timezone)
        return u'{0}, {1} at {2}'.format(self.study_group.course.title, self.meeting_datetime(), self.study_group.venue_name)

    def to_json(self):
        data = {
            'study_group': self.study_group.pk,
            'meeting_date': self.meeting_date,
            'meeting_time': self.meeting_time
        }
        return json.dumps(data, cls=DjangoJSONEncoder)


class Reminder(models.Model):
    study_group = models.ForeignKey('studygroups.StudyGroup') #TODO redundant field
    study_group_meeting = models.ForeignKey('studygroups.StudyGroupMeeting', blank=True, null=True)
    email_subject = models.CharField(max_length=256)
    email_body = models.TextField()
    sms_body = models.CharField(verbose_name=_('SMS (Text)'), max_length=160)

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)


class Rsvp(models.Model):
    study_group_meeting = models.ForeignKey('studygroups.StudyGroupMeeting')
    application = models.ForeignKey('studygroups.Application')
    attending = models.BooleanField()

    def __unicode__(self):
        return u'{0} ({1})'.format(self.application, 'yes' if self.attending else 'no')


class Feedback(LifeTimeTrackingModel):

    BAD = '1'
    NOT_SO_GOOD = '2'
    GOOD = '3'
    WELL = '4'
    GREAT = '5'

    RATING = [
        (GREAT, _('Great')),
        (WELL, _('Pretty well')),
        (GOOD, _('Good')),
        (NOT_SO_GOOD, _('Not so great')),
        (BAD, _('I need some help')),
    ]

    study_group_meeting = models.ForeignKey('studygroups.StudyGroupMeeting') # TODO should this be a OneToOneField?
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


def generate_all_meetings(study_group):
    if StudyGroupMeeting.objects.filter(study_group=study_group).exists():
        raise Exception(_('Meetings already exist for this study group'))

    meeting_date = study_group.start_date
    while meeting_date <= study_group.end_date:
        meeting = StudyGroupMeeting(
            study_group=study_group,
            meeting_date=meeting_date,
            meeting_time=study_group.meeting_time
        )
        meeting.save()
        meeting_date += datetime.timedelta(days=7)


# If called directly, be sure to activate the current language
def generate_reminder(study_group):
    now = timezone.now()
    next_meeting = study_group.next_meeting()
    if next_meeting and next_meeting.meeting_datetime() - now < datetime.timedelta(days=4):
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
            previous_meeting = study_group.studygroupmeeting_set.filter(meeting_date__lt=next_meeting.meeting_date).order_by('meeting_date').last()
            if previous_meeting and previous_meeting.feedback_set.first():
                context['feedback'] = previous_meeting.feedback_set.first()
            # send PDF survey if this is the final weeks meeting
            last_meeting = study_group.studygroupmeeting_set.active().order_by('-meeting_date', '-meeting_time').first()
            context['is_last_meeting'] = last_meeting.pk == next_meeting.pk
            timezone.activate(pytz.timezone(study_group.timezone))
            #TODO do I need to activate a locale?
            reminder.email_subject = render_to_string(
                'studygroups/email/reminder-subject.txt',
                context
            )
            reminder.email_body = render_to_string(
                'studygroups/email/reminder.txt',
                context
            )
            reminder.sms_body = render_to_string(
                'studygroups/email/sms.txt',
                context
                )
            # TODO - handle SMS reminders that are too long
            if len(reminder.sms_body) > 160:
                logger.error('SMS body too long: ' + reminder.sms_body)
            reminder.sms_body = reminder.sms_body[:160]
            reminder.save()

            facilitator_notification_subject = u'A reminder for {0} was generated'.format(study_group.course.title)
            facilitator_notification_html = render_to_string(
                'studygroups/email/reminder_notification.html',
                context
            )
            facilitator_notification_txt = render_to_string(
                'studygroups/email/reminder_notification.txt',
                context
            )
            timezone.deactivate()
            to = [study_group.facilitator.email]
            # TODO remove admin here, don't need to get these updates
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


# If called directly, be sure to activate the current language
# Should be called every 15 minutes starting just after the hour
def send_survey_reminder(study_group):
    now = timezone.now()
    ## last :00, :15, :30 or :45
    last_15 = now.replace(minute=now.minute//15*15, second=0)
    last_meeting = study_group.studygroupmeeting_set.active().order_by('-meeting_date', '-meeting_time').first()

    if last_meeting and last_15 - datetime.timedelta(minutes=15) <= last_meeting.meeting_datetime() and last_meeting.meeting_datetime() < last_15:
        slug = '{}-{}'.format(slugify(study_group.venue_name), study_group.id)
        learning_circle_text = "{} at {} ({})".format(study_group.course.title, study_group.venue_name, slug)
        context = {
            'learning_circle':  urllib.quote(learning_circle_text)
        }
        subject = render_to_string(
            'studygroups/email/learner_survey_reminder-subject.txt',
            context
        )
        html = render_to_string(
            'studygroups/email/learner_survey_reminder.html',
            context
        )
        txt = render_to_string(
            'studygroups/email/learner_survey_reminder.txt',
            context
        )
        timezone.deactivate()
        to = []
        applications = study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')
        bcc = [su.email for su in applications]
        notification = EmailMultiAlternatives(
            subject.strip(),
            txt,
            settings.SERVER_EMAIL,
            to,
            bcc
        )
        notification.attach_alternative(html, 'text/html')
        notification.send()


# If called directly, be sure to activate the current language
# Should be called once a day minutes starting just after the hour
def send_facilitator_survey(study_group):
    """ send survey to all facilitators if their last study group meetings was a week ago """
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    last_week = today - datetime.timedelta(days=7);
    last_meeting = study_group.studygroupmeeting_set.active()\
            .order_by('-meeting_date', '-meeting_time').first()

    if last_meeting and last_week <= last_meeting.meeting_datetime() and last_meeting.meeting_datetime() < last_week + datetime.timedelta(days=1):
        slug = '{}-{}'.format(slugify(study_group.venue_name), study_group.id)
        learning_circle_text = "{} at {} ({})".format(study_group.course.title, study_group.venue_name, slug)
        context = {
            'learning_circle_slug':  urllib.quote(learning_circle_text)
        }
        timezone.deactivate()
        subject, txt, html = render_email_templates(
            'studygroups/email/facilitator-survey',
            context
        )
        to = [study_group.facilitator.email]
        applications = study_group.application_set.active()\
            .filter(accepted_at__isnull=False).exclude(email='')

        notification = EmailMultiAlternatives(
            subject,
            txt,
            settings.SERVER_EMAIL,
            to
        )
        notification.attach_alternative(html, 'text/html')
        notification.send()







# If called directly, be sure to activate language to use for constructing URLs
# Failed text delivery won't case this function to fail, simply log an error
def send_reminder(reminder):
    to = [su.email for su in reminder.study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')]
    if reminder.study_group_meeting:
        # this is a reminder and we need RSVP links
        for email in to:
            yes_link = reminder.study_group_meeting.rsvp_yes_link(email)
            no_link = reminder.study_group_meeting.rsvp_no_link(email)
            application = reminder.study_group_meeting.study_group.application_set.active().filter(email__iexact=email).first()
            unsubscribe_link = application.unapply_link()
            email_body = reminder.email_body
            email_body = re.sub(r'\(<!--RSVP:YES-->.*\)', yes_link, email_body)
            email_body = re.sub(r'\(<!--RSVP:NO-->.*\)', no_link, email_body)
            email_body = re.sub(r'\(<!--UNSUBSCRIBE-->.*\)', unsubscribe_link, email_body)
            send_mail(
                reminder.email_subject.strip('\n'),
                email_body,
                reminder.study_group.facilitator.email,
                [email],
                fail_silently=False
            )
        # Send to organizer without RSVP & unsubscribe links
        send_mail(
            reminder.email_subject.strip('\n'),
            reminder.email_body,
            reminder.study_group.facilitator.email,
            [reminder.study_group.facilitator.email],
            fail_silently=False
        )
    else:
        email_body = reminder.email_body
        # TODO i18n
        email_body = u'{0}\n\nTo leave this Learning Circle you can visit https://{1}{2}'.format(email_body, settings.DOMAIN, reverse('studygroups_optout'))
        # TODO - all emails should contain the unsubscribe link
        to += [reminder.study_group.facilitator.email]
        reminder_email = EmailMultiAlternatives(
            reminder.email_subject.strip('\n'),
            email_body,
            reminder.study_group.facilitator.email,
            [],
            bcc=to,
        )
        reminder_email.send()

    # send SMS
    tos = [su.mobile for su in reminder.study_group.application_set.active().filter(accepted_at__isnull=False).exclude(mobile='')]
    for to in tos:
        try:
            #TODO - insert opt out link
            #if reminder.study_group_meeting:
            send_message(to, reminder.sms_body)
        except TwilioRestException as e:
            logger.exception(u"Could not send text message to %s", to, exc_info=e)

    reminder.sent_at = timezone.now()
    reminder.save()


def create_rsvp(contact, study_group, meeting_datetime, attending):
    # expect meeting_date as python datetime
    # contact is an email address of mobile number
    # study_group is the study group id
    study_group_meeting = StudyGroupMeeting.objects.get(study_group__id=study_group, meeting_date=meeting_datetime.date(), meeting_time=meeting_datetime.time())
    application = None
    if '@' in contact:
        application = Application.objects.active().get(study_group__id=study_group, email__iexact=contact)
    else:
        application = Application.objects.active().get(study_group__id=study_group, mobile=contact)
    rsvp = Rsvp.objects.all().filter(study_group_meeting=study_group_meeting, application=application).first()
    if not rsvp:
        rsvp = Rsvp(study_group_meeting=study_group_meeting, application=application, attending=attending=='yes')
    else:
        rsvp.attending = attending=='yes'
    rsvp.save()
    return rsvp


def report_data(start_time, end_time, team=None):
    """ Return data for the indicated time period

    If team is given, study groups will be filtered by team
    """
    study_groups = StudyGroup.objects.active()
    meetings = StudyGroupMeeting.objects.active()\
            .filter(meeting_date__gte=start_time, meeting_date__lt=end_time)\
            .filter(study_group__in=study_groups)

    new_study_groups = StudyGroup.objects.active()\
            .filter(created_at__gte=start_time, created_at__lt=end_time)
    new_facilitators = User.objects.filter(date_joined__gte=start_time, date_joined__lt=end_time)
    logins = User.objects.filter(last_login__gte=start_time, last_login__lt=end_time)
    signups = Application.objects.active().filter(created_at__gte=start_time, created_at__lt=end_time)

    if team:
        members = team.teammembership_set.all().values('user')
        meetings = meetings.filter(study_group__facilitator__in=members)
        new_study_groups = new_study_groups.filter(facilitator__in=members)
        logins = logins.filter(pk__in=members)
        signups = signups.filter(study_group__facilitator__in=members)

    feedback = Feedback.objects.filter(study_group_meeting__in=meetings)

    report = {
        'meetings': meetings,
        'feedback': feedback,
        'study_groups': new_study_groups,
        'facilitators': new_facilitators,
        'logins': logins,
        'signups': signups,
    }
    if team:
        report['team'] = team
    return report


def send_weekly_update():
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = today - datetime.timedelta(days=today.weekday()+7) #start of previous week
    end_time = start_time + datetime.timedelta(days=7)
    context = {
        'start_time': start_time,
        'end_time': end_time,
        'protocol': 'https',
        'domain': settings.DOMAIN,
    }

    for team in Team.objects.all():
        report_context = report_data(start_time, end_time, team)
        report_context.update(context)
        timezone.activate(pytz.timezone(settings.TIME_ZONE)) #TODO not sure what this influences anymore?
        translation.activate(settings.LANGUAGE_CODE)
        html_body = render_to_string('studygroups/email/weekly-update.html', report_context)
        text_body = render_to_string('studygroups/email/weekly-update.txt', report_context)
        timezone.deactivate()
 
        to = [o.user.email for o in team.teammembership_set.filter(role=TeamMembership.ORGANIZER)]
        # TODO, extract this to make delegating to celery in the future easier
        update = EmailMultiAlternatives(
            _('Weekly Learning Circles update'),
            text_body,
            settings.SERVER_EMAIL,
            to
        )
        update.attach_alternative(html_body, 'text/html')
        update.send()

    # send weekly update to staff
    report_context = report_data(start_time, end_time)
    report_context.update(context)
    timezone.activate(pytz.timezone(settings.TIME_ZONE)) 
    translation.activate(settings.LANGUAGE_CODE)
    html_body = render_to_string('studygroups/email/weekly-update.html', report_context)
    text_body = render_to_string('studygroups/email/weekly-update.txt', report_context)
    timezone.deactivate()
 
    to = [o.email for o in User.objects.filter(is_staff=True)]
    update = EmailMultiAlternatives(
        _('Weekly Learning Circles update'),
        text_body,
        settings.SERVER_EMAIL,
        to
    )
    update.attach_alternative(html_body, 'text/html')
    update.send()


def send_new_facilitator_email(facilitator):
    context = {
        'facilitator': facilitator
    }

    timezone.activate(pytz.timezone(settings.TIME_ZONE))
    translation.activate(settings.LANGUAGE_CODE)
    subject = render_to_string('studygroups/email/new_facilitator_update-subject.txt', context).strip('\n')
    html_body = render_to_string('studygroups/email/new_facilitator_update.html', context)
    text_body = render_to_string('studygroups/email/new_facilitator_update.txt', context)
    timezone.deactivate()
    to = [facilitator.email]
 
    msg = EmailMultiAlternatives(subject, text_body, settings.SERVER_EMAIL, to)
    msg.attach_alternative(html_body, 'text/html')
    msg.send()


def send_new_studygroup_email(studygroup):
    context = {
        'studygroup': studygroup
    }

    timezone.activate(pytz.timezone(settings.TIME_ZONE))
    translation.activate(settings.LANGUAGE_CODE)
    subject = render_to_string('studygroups/email/new_studygroup_update-subject.txt', context).strip('\n')
    html_body = render_to_string('studygroups/email/new_studygroup_update.html', context)
    text_body = render_to_string('studygroups/email/new_studygroup_update.txt', context)
    timezone.deactivate()
    to = [studygroup.facilitator.email]
 
    msg = EmailMultiAlternatives(subject, text_body, settings.SERVER_EMAIL, to)
    msg.attach_alternative(html_body, 'text/html')
    msg.send()


def send_team_invitation_email(team, email, organizer):
    """ Send email to new or existing facilitators """
    """ organizer should be a User object """
    user_qs = User.objects.filter(email__iexact=email)
    context = {
        "team": team,
        "organizer": organizer,
        "domain": "learningcircles.p2pu.org"
    }

    if user_qs.count() == 0:
        # invite user to join 
        subject = render_to_string('studygroups/email/new_facilitator_invite-subject.txt', context).strip('\n')
        html_body = render_to_string('studygroups/email/new_facilitator_invite.html', context)
        text_body = render_to_string('studygroups/email/new_facilitator_invite.txt', context)
    else:
        context['user'] = user_qs.get()
        subject = render_to_string('studygroups/email/team_invite-subject.txt', context).strip('\n')
        html_body = render_to_string('studygroups/email/team_invite.html', context)
        text_body = render_to_string('studygroups/email/team_invite.txt', context)

    to = [email]
    from_ = organizer.email
 
    msg = EmailMultiAlternatives(subject, text_body, from_, to)
    msg.attach_alternative(html_body, 'text/html')
    msg.send()


def get_study_group_organizers(study_group):
    """ Return the organizers for the study group """
    team_membership = TeamMembership.objects.filter(user=study_group.facilitator)
    if team_membership.count() == 1:
        organizers = team_membership.first().team.teammembership_set.filter(role=TeamMembership.ORGANIZER).values('user')
        return User.objects.filter(pk__in=organizers)
    return []


def get_team_users(user):
    """ Return the team members for a user """
    # TODO this function doesn't make sense - only applies for logged in users
    # change functionality or rename to get_team_mates
    team_membership = TeamMembership.objects.filter(user=user)
    if team_membership.count() == 1:
        members = team_membership.first().team.teammembership_set.values('user')
        return User.objects.filter(pk__in=members)
    return []


""" Return the team a user belongs to """
def get_user_team(user):
    team_membership = TeamMembership.objects.filter(user=user).get()
    return team_membership.team
