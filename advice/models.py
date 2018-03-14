# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Advice(models.Model):
    first_name = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    country = models.CharField(max_length=256)
    topic = models.CharField(max_length=256)
    tip = models.CharField(max_length=1024)

    def __str__(self):
        return self.tip
