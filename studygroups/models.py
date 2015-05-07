from django.db import models
from django.db.models.signals import post_init
from django.utils import timezone

from s3direct.fields import S3DirectField

import calendar
import datetime
import pytz

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
    caption = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title


class StudyGroup(models.Model):
    name = models.CharField(max_length=128, default=_study_group_name)
    course = models.ForeignKey('studygroups.Course')
    location = models.CharField(max_length=128)
    location_link = models.URLField()
    day = models.CharField(max_length=128, choices=zip(calendar.day_name, calendar.day_name))
    time = models.TimeField()
    timezone = models.CharField(max_length=128)
    max_size = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'{0} - {1}s {2} at the {3}'.format(self.course.title, self.day, self.time, self.location)

#TODO - remove Text or Phone
PREFERRED_CONTACT_METHOD = [
    ('Email', 'Email'),
    ('Text', 'Text'),
]

COMPUTER_ACCESS = [
    ('No', 'No'),
    ('Sometimes', 'Sometimes'),
    ('Yes', 'Yes'),
]


class Application(models.Model):
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
        return u"{0}".format(self.name)


#class Reminder(models.Model):
#    study_group = models.ForeignKey('studygroups.StudyGroup')
#    meeting_time = models.DateTimeField()



def accept_application(application):
    # add a study group application to a study group
    application.accepted_at = timezone.now()
    application.save()


def next_meeting_date(study_group):
    now = timezone.now()
    day_delta = list(calendar.day_name).index(study_group.day) - now.weekday()
    time = study_group.time
    date = now + datetime.timedelta(days=day_delta)
    meeting_datetime = datetime.datetime(
        date.year, date.month, date.day,
        time.hour, time.minute, time.second, 0,
        pytz.timezone(study_group.timezone)
    )
    if meeting_datetime < now:
        meeting_datetime = meeting_datetime + datetime.timedelta(weeks=1)
    return meeting_datetime


def generate_reminders(study_group):
    now = timezone.now()
    if next_meeting_date - now < datetime.timedelta(days=3):
        # check if a notifcation already exists for this meeting
        study_group.reminders.filter(meeting_time=next_meeting_date)

