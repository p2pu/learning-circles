from django.db import models
from django.contrib.auth.models import User

from studygroups.models.base import Moderatable

import pytz


class Event(Moderatable):
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=500)
    created_by = models.ForeignKey(User)

    datetime = models.DateTimeField()
    timezone = models.CharField(max_length=128)

    city = models.CharField(max_length=256, blank=True)
    region = models.CharField(max_length=256, blank=True)
    country = models.CharField(max_length=256, blank=True)
    country_en = models.CharField(max_length=256, blank=True)
    #place_id ??

    link = models.URLField()
    image = models.ImageField(blank=True)

    def local_datetime(self):
        tz = pytz.timezone(self.timezone)
        return self.datetime.astimezone(tz)


