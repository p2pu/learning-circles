# coding=utf-8
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse  # TODO ideally this shouldn't be in the model
from django_bleach.models import BleachField

from studygroups.utils import gen_unsubscribe_querystring
from studygroups.utils import gen_rsvp_querystring
from studygroups.utils import render_to_string_ctx
from studygroups.utils import use_language

from celery import current_app

from .base import SoftDeleteQuerySet
from .base import LifeTimeTrackingModel
from .course import Course

from functools import reduce
import calendar
import datetime
import pytz
import json
import uuid
import random
import string


# TODO remove organizer model - only use Facilitator model + Team Membership
class Organizer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.__str__()


class StudyGroupQuerySet(SoftDeleteQuerySet):

    def published(self):
        """ exclude drafts from public learning circles """
        return self.active().filter(draft=False)


class StudyGroup(LifeTimeTrackingModel):
    name = models.CharField(max_length=128, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = BleachField(max_length=2000, blank=True, allowed_tags=settings.TINYMCE_DEFAULT_CONFIG.get('valid_elements', '').split(','), allowed_attributes={'a': ['href', 'title', 'rel', 'target']})
    course_description = BleachField(max_length=2000, blank=True, allowed_tags=settings.TINYMCE_DEFAULT_CONFIG.get('valid_elements', '').split(','), allowed_attributes={'a': ['href', 'title', 'rel', 'target']})
    venue_name = models.CharField(max_length=256)
    venue_address = models.CharField(max_length=256)
    venue_details = models.CharField(max_length=128)
    venue_website = models.URLField(max_length=256, blank=True)
    city = models.CharField(max_length=256)
    region = models.CharField(max_length=256, blank=True)  # schema.org. Algolia => administrative
    country = models.CharField(max_length=256, blank=True)
    country_en = models.CharField(max_length=256, blank=True)
    language = models.CharField(max_length=6)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    place_id = models.CharField(max_length=256, blank=True)  # Algolia place_id
    online = models.BooleanField(default=False) # indicate if the meetings will take place online
    facilitator = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()  # This field caches first_meeting.meeting_date
    meeting_time = models.TimeField()
    end_date = models.DateField()  # This field caches last_meeting.meeting_date
    duration = models.PositiveIntegerField(default=90)  # meeting duration in minutes
    timezone = models.CharField(max_length=128)
    signup_open = models.BooleanField(default=True)
    draft = models.BooleanField(default=True)
    image = models.ImageField(blank=True)
    signup_question = models.CharField(max_length=256, blank=True)
    facilitator_goal = models.CharField(max_length=256, blank=True)
    facilitator_concerns = models.CharField(max_length=256, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    facilitator_rating = models.IntegerField(blank=True, null=True)  # Deprecated: 1-5 rating use previously
    facilitator_goal_rating = models.IntegerField(blank=True, null=True)  # Self reported rating of whether the facilitator goal was met.
    course_rating = models.IntegerField(blank=True, null=True)
    course_rating_reason = models.TextField(blank=True)

    attach_ics = models.BooleanField(default=True) # TODO Remove this
    did_not_happen = models.NullBooleanField(blank=True, null=True)  # Used by the facilitator to report if the learning circle didn't happen
    learner_survey_sent_at = models.DateTimeField(blank=True, null=True)
    facilitator_survey_sent_at = models.DateTimeField(blank=True, null=True)

    objects = StudyGroupQuerySet.as_manager()

    def save(self, *args, **kwargs):
        # use course.caption if course_description is not set
        if self.course_description is None:
            self.course_description = self.course.caption
        # use course.title if name is not set
        if self.name is None:
            self.name = self.course.title
        super().save(*args, **kwargs)

    def day(self):
        return calendar.day_name[self.start_date.weekday()]

    def end_time(self):
        q = datetime.datetime.combine(self.start_date, self.meeting_time) + datetime.timedelta(minutes=self.duration)
        return q.time()

    def next_meeting(self):
        now = timezone.now()
        meeting_list = self.meeting_set.active().order_by('meeting_date', 'meeting_time')
        return next((m for m in meeting_list if m.meeting_datetime() > now), None)

    def local_start_date(self):
        tz = pytz.timezone(self.timezone)
        date = datetime.datetime.combine(self.start_date, self.meeting_time)
        return tz.localize(date)

    def timezone_display(self):
        # NOTE: This only applies to the first meeting!
        return self.local_start_date().strftime("%Z")

    def last_meeting(self):
        return self.meeting_set.active().order_by('-meeting_date', '-meeting_time').first()

    def first_meeting(self):
        return self.meeting_set.active().order_by('meeting_date', 'meeting_time').first()

    def report_url(self):
        base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
        path = reverse('studygroups_final_report', kwargs={'study_group_id': self.id})
        return base_url + path

    def signup_url(self):
        return f"{settings.PROTOCOL}://{settings.DOMAIN}" + reverse('studygroups_signup', args=(slugify(self.venue_name, allow_unicode=True), self.id,))

    def can_update_meeting_datetime(self):
        """ check to see if you can update the date """
        # if it's a draft, you can edit
        if self.draft is True:
            return True

        # if there are no meetings, you can edit
        meeting_list = self.meeting_set.active().order_by('meeting_date', 'meeting_time')
        if meeting_list.count() == 0:
            return True

        # if the first meeting is more than 2 days from now, you can edit
        two_days_from_now = timezone.now() + datetime.timedelta(days=2)
        if meeting_list.first().meeting_datetime() > two_days_from_now:
            return True

        return False


    @property
    def meets_weekly(self):
        meeting_dates = self.meeting_set.active().order_by('meeting_date', 'meeting_time').values_list('meeting_date', flat=True)
        if len(meeting_dates) == 0:
            return False
        # check that meeting dates are spaced 7 days
        lds = reduce(lambda x,y: y if x and y-x==datetime.timedelta(days=7) else False, meeting_dates)
        return lds and True


    def feedback_status(self):
        if self.facilitator_goal_rating and self.course_rating and self.course_rating_reason or self.facilitatorsurveyresponse_set.count():
            return 'done'
        last_meeting = self.last_meeting()
        if last_meeting and timezone.now() < last_meeting.meeting_datetime():
            return 'pending'
        return 'todo'



    @property
    def weeks(self):
        return (self.end_date - self.start_date).days//7 + 1

    def to_dict(self):
        sg = self  # TODO - this logic is repeated in the API class
        data = {
            "id": sg.pk,
            "name": sg.name,
            "course": sg.course.id,
            "course_title": sg.course.title,
            "description": sg.description,
            "course_description": sg.course_description,
            "venue_name": sg.venue_name,
            "venue_details": sg.venue_details,
            "venue_address": sg.venue_address,
            "venue_website": sg.venue_website,
            "city": sg.city,
            "region": sg.region,
            "country": sg.country,
            "country_en": sg.country_en,
            "latitude": sg.latitude,
            "longitude": sg.longitude,
            "place_id": sg.place_id,
            "online": sg.online,
            "language": sg.language,
            "start_date": sg.start_date,
            "start_datetime": self.local_start_date(),
            "weeks": sg.weeks,
            "meeting_time": sg.meeting_time.strftime('%H:%M'),
            "duration": sg.duration,
            "timezone": sg.timezone,
            "timezone_display": sg.timezone_display(),
            "signup_question": sg.signup_question,
            "facilitator_goal": sg.facilitator_goal,
            "facilitator_concerns": sg.facilitator_concerns,
            "day": sg.day(),
            "end_time": sg.end_time(),
            "facilitator": sg.facilitator.first_name + " " + sg.facilitator.last_name,
            "signup_count": sg.application_set.active().count(),
            "draft": sg.draft,
            "url": reverse('studygroups_view_study_group', args=(sg.id,)),
            "signup_url": reverse('studygroups_signup', args=(slugify(sg.venue_name, allow_unicode=True), sg.id,)),
        }
        next_meeting = self.next_meeting()
        if next_meeting:
            data['next_meeting_date'] = next_meeting.meeting_date
        if sg.image:
            data["image_url"] = sg.image.url
        return data

    def to_json(self):
        return json.dumps(self.to_dict(), cls=DjangoJSONEncoder)

    def __str__(self):
        return '{0} - {1}s {2} at the {3}'.format(self.name, self.day(), self.meeting_time, self.venue_name)


class Application(LifeTimeTrackingModel):
    study_group = models.ForeignKey('studygroups.StudyGroup', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    email = models.EmailField(verbose_name='Email address', blank=True)
    communications_opt_in = models.BooleanField(default=False)
    mobile = models.CharField(max_length=20, blank=True)
    mobile_opt_out_at = models.DateTimeField(blank=True, null=True)
    signup_questions = models.TextField(default='{}')
    goal_met = models.SmallIntegerField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    anonymized = models.BooleanField(default=False)

    def __str__(self):
        return "{0} <{1}>".format(self.name, self.email if self.email else self.mobile)

    def unapply_link(self):
        base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
        url = reverse('studygroups_leave')
        qs = gen_unsubscribe_querystring(self.pk)
        return '{0}{1}?{2}'.format(base_url, url, qs)

    def get_signup_questions(self):
        return json.loads(self.signup_questions)

    def get_goal(self):
        goal = self.get_signup_questions().get('goals')
        if goal:
            goal = goal.replace('Other: ', '')
        return goal

    def anonymize(self):
        self.mobile = ''
        self.name = 'Anonymous ' + random.choice(['Penguin', 'Albatross', 'Elephant', 'Dassie', 'Lion', 'Sponge', 'Giraffe', 'Hippo', 'Leopard', 'Buffalo', 'Crab', 'Snail'])
        email_part = "".join([random.choice(string.digits+string.ascii_letters) for i in range(12)])
        self.email = 'devnull.{}@localhost'.format(email_part)
        self.anonymized = True
        self.save()

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
        ('0', _('Can\'t do')),
        ('1', _('Need help doing')),
        ('2', _('Can do with difficulty')),
        ('3', _('Can do')),
        ('4', _('Expert (can teach others)')),
    )

    def digital_literacy_for_display(self):
        answers = json.loads(self.signup_questions)
        return { q: {'question_text': text, 'answer': answers.get(q), 'answer_text': dict(self.DIGITAL_LITERACY_CHOICES).get(answers.get(q)) if q in answers else ''} for q, text in list(self.DIGITAL_LITERACY_QUESTIONS.items()) if answers.get(q) }


class Meeting(LifeTimeTrackingModel):
    study_group = models.ForeignKey('studygroups.StudyGroup', on_delete=models.CASCADE)
    meeting_date = models.DateField()
    meeting_time = models.TimeField()
    wrapup_sent_at = models.DateTimeField(blank=True, null=True)
    recap = models.ForeignKey('studygroups.Reminder', null=True, blank=True, on_delete=models.SET_NULL)
    recap_dismissed = models.BooleanField(default=False)
    #reminder_deleted_at = models.DateTimeField(blank=True, null=True) # used to indicate manual deletion of a reminder

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_meeting_date = self.meeting_date
        self._original_meeting_time = self.meeting_time

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)

        if self.study_group.meeting_set.active().count():
            self.study_group.start_date = self.study_group.first_meeting().meeting_date
            self.study_group.end_date = self.study_group.last_meeting().meeting_date
            self.study_group.save()

        rescheduled = any([
            self._original_meeting_time != self.meeting_time,
            self._original_meeting_date != self.meeting_date,
        ])
        deleted = self.deleted_at

        if rescheduled or created or deleted:

            if self.reminder_set.filter(sent_at__isnull=False).count() == 1:
                # a reminder has been sent, disassociate it
                self.reminder_set.update(study_group_meeting=None)
         
                tz = pytz.timezone(self.study_group.timezone)
                original_meeting_datetime = tz.localize(
                    datetime.datetime.combine(self._original_meeting_date, self._original_meeting_time)
                )
         
                # the previous date was in the future
                if original_meeting_datetime > timezone.now():
                    # send meeting change notification
                    current_app.send_task('studygroups.tasks.send_meeting_change_notification', (self.pk, original_meeting_datetime))
            else:
                # no reminder has been sent
                # deleted reminder if any
                self.reminder_set.all().delete()
         
            # generate a reminder if the meeting is in the future
            if self.meeting_datetime() > timezone.now() and not self.deleted_at:
                generate_meeting_reminder(self)


    def meeting_number(self):
        # TODO this will break for two meetings on the same day
        return Meeting.objects.active().filter(meeting_date__lte=self.meeting_date, study_group=self.study_group).count()

    def meeting_datetime(self):
        tz = pytz.timezone(self.study_group.timezone)
        return tz.localize(datetime.datetime.combine(self.meeting_date, self.meeting_time))

    def meeting_datetime_end(self):
        tz = pytz.timezone(self.study_group.timezone)
        start = tz.localize(datetime.datetime.combine(self.meeting_date, self.meeting_time))
        return start + datetime.timedelta(minutes=self.study_group.duration)


    def send_reminder_at(self):
        """ The datetime that a reminder should be sent at """
        previous_meeting = self.study_group.meeting_set.active().filter(
            models.Q(meeting_date__lt=self.meeting_date)
            | models.Q(meeting_date=self.meeting_date, meeting_time__lt=self.meeting_time)
        ).order_by('-meeting_date', '-meeting_time').first()
        two_days_before = self.meeting_datetime() - datetime.timedelta(days=2)
        # ensure send_at is always after previous meeting finished
        tz = pytz.timezone(self.study_group.timezone)
        # subtract 5 seconds from now so that a past date technically stays in the past and can be sent
        now = timezone.now().astimezone(tz) - datetime.timedelta(seconds=5)
        if previous_meeting:
            return max(now, max(two_days_before, previous_meeting.meeting_datetime() + datetime.timedelta(minutes=self.study_group.duration)))
        return max(now, two_days_before)


    def rsvps(self):
        rsvp_set = self.rsvp_set.all().select_related('application').order_by('application__name').filter(application__deleted_at__isnull=True)
        return {
            'yes': rsvp_set.filter(attending=True),
            'no': rsvp_set.filter(attending=False),
        }

    def rsvp_pending(self):
        return self.study_group.application_set.active().exclude(id__in=self.rsvp_set.all().values('application_id')).order_by('name')

    def rsvp_yes_link(self, email):
        base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
        url = reverse('studygroups_rsvp')
        yes_qs = gen_rsvp_querystring(
            email,
            self.study_group.pk,
            self.meeting_datetime(),
            'yes'
        )
        return '{0}{1}?{2}'.format(base_url, url, yes_qs)

    def rsvp_no_link(self, email):
        base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
        url = reverse('studygroups_rsvp')
        no_qs = gen_rsvp_querystring(
            email,
            self.study_group.pk,
            self.meeting_datetime(),
            'no'
        )
        return '{0}{1}?{2}'.format(base_url, url, no_qs)

    def status(self):
        if self.meeting_datetime() > timezone.now() and self != self.study_group.next_meeting() or self.study_group.draft:
            return 'pending'

        if self.feedback_set.count() and (self.recap_dismissed or self.recap):
            return 'done'

        return 'todo'

    def __str__(self):
        # TODO i18n
        return '{0}, {1} at {2}'.format(self.study_group.name, self.meeting_datetime(), self.study_group.venue_name)

    def to_json(self):
        data = {
            'study_group': self.study_group.pk,
            'meeting_date': self.meeting_date,
            'meeting_time': self.meeting_time
        }
        return json.dumps(data, cls=DjangoJSONEncoder)


class Reminder(models.Model):
    study_group = models.ForeignKey('studygroups.StudyGroup', on_delete=models.CASCADE)
    study_group_meeting = models.ForeignKey('studygroups.Meeting', blank=True, null=True, on_delete=models.CASCADE)  # TODO rename to meeting. Make OneToOne?
    email_subject = models.CharField(max_length=256)
    email_body = BleachField(max_length=4000, allowed_tags=settings.TINYMCE_DEFAULT_CONFIG.get('valid_elements', '').split(',') + ['br'], allowed_attributes={'a': ['href', 'title', 'rel', 'target']})
    sms_body = models.CharField(verbose_name=_('SMS (Text)'), max_length=160, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    def sent_at_tz(self):
        tz = pytz.timezone(self.study_group.timezone)
        return self.sent_at.astimezone(tz)

    def send_at(self):
        if self.sent_at:
            return self.sent_at_tz()

        if not self.study_group_meeting:
            # Messages shouldn't exist that hasn't been sent without an associated meeting
            #raise Exception('Data inconsistency')
            # update: unsent follow ups could match this codepath
            # TODO will this be in the wrong timezone?
            return timezone.now()

        return self.study_group_meeting.send_reminder_at()


def generate_meeting_reminder(meeting):
    if Reminder.objects.filter(study_group_meeting=meeting).exists():
        return None

    reminder = Reminder()
    reminder.study_group = meeting.study_group
    reminder.study_group_meeting = meeting
    context = {
        'facilitator': meeting.study_group.facilitator,
        'study_group': meeting.study_group,
        'next_meeting': meeting,
        'reminder': reminder,
    }
    timezone.activate(pytz.timezone(meeting.study_group.timezone))
    with use_language(meeting.study_group.language):
        reminder.email_subject = render_to_string_ctx(
            'studygroups/email/meeting_reminder-subject.txt',
            context
        ).strip('\n')
        reminder.email_body = render_to_string_ctx(
            'studygroups/email/meeting_reminder.html',
            context
        )
        reminder.sms_body = render_to_string_ctx(
            'studygroups/email/meeting_reminder-sms.txt',
            context
        )
    # TODO - handle SMS reminders that are too long
    if len(reminder.sms_body) > 160:
        logger.error('SMS body too long: ' + reminder.sms_body)
    reminder.sms_body = reminder.sms_body[:160]
    reminder.save()
    return reminder


class Rsvp(models.Model):
    study_group_meeting = models.ForeignKey('studygroups.Meeting', on_delete=models.CASCADE) # TODO rename to meeting
    application = models.ForeignKey('studygroups.Application', on_delete=models.CASCADE)
    attending = models.BooleanField()

    def __str__(self):
        return '{0} ({1})'.format(self.application, 'yes' if self.attending else 'no')


class Feedback(LifeTimeTrackingModel):

    AWFUL = '1'
    NOT_SO_GOOD = '2'
    OKAY = '3'
    WELL = '4'
    GREAT = '5'

    RATING = [
        (GREAT, _('Great')),
        (WELL, _('Pretty well')),
        (OKAY, _('Okay')),
        (NOT_SO_GOOD, _('Not so good')),
        (AWFUL, _('Awful')),
    ]

    study_group_meeting = models.ForeignKey('studygroups.Meeting', on_delete=models.CASCADE) # TODO should this be a OneToOneField?
    feedback = models.TextField(blank=True) # Shared with learners. This is being deprecated, but kept for retaining past data.
    attendance = models.PositiveIntegerField(blank=True, null=True)
    reflection = models.TextField(blank=True) # Shared with team and P2PU
    rating = models.CharField(choices=RATING, max_length=16, blank=True)

    def reflection_json(self):
        if self.reflection:
            return json.loads(self.reflection)
        else:
            return {}
