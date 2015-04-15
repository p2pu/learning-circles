from django.db import models
from django.db.models.signals import post_init
from django.dispatch import receiver

from s3direct.fields import S3DirectField

import calendar

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
    time = models.CharField(max_length=128)
    max_size = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'{0} - {1} - {2} ({3})'.format(self.name, self.course.title, self.time, self.studygroupsignup_set.count())

PREFERRED_CONTACT_METHOD = [
    ('Email', 'Email'),
    ('Text', 'Text'),
    ('Phone', 'Phone'),
]

COMPUTER_ACCESS = [
    ('Yes', 'Yes'),
    ('No', 'No'),
    ('Sometimes', 'Sometimes')
]

class Application(models.Model):
    name = models.CharField(max_length=128)
    email = models.EmailField()
    mobile = models.CharField(max_length=20, null=True, blank=True)
    contact_method = models.CharField(max_length=128, choices=PREFERRED_CONTACT_METHOD)
    computer_access = models.CharField(max_length=128, choices=COMPUTER_ACCESS)
    study_groups = models.ManyToManyField('studygroups.StudyGroup')
    goals = models.TextField()
    support = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


class StudyGroupSignup(models.Model):
    study_group = models.ForeignKey('studygroups.StudyGroup')
    username = models.CharField(max_length=128)
    email = models.EmailField()
    mobile = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{0} - {1}".format(self.username, self.study_group.name)

    class Meta:
        unique_together = ("email", "study_group")
