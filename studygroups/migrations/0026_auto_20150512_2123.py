# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0025_reminder'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='duration',
            field=models.IntegerField(default=120),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studygroup',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 12, 21, 23, 30, 288073, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studygroup',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 12, 21, 23, 38, 459528, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
