# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0031_location_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studygroup',
            name='day',
        ),
        migrations.RemoveField(
            model_name='studygroup',
            name='time',
        ),
    ]
