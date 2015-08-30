# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0034_create_facilitators_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='attendance',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='redyellowgreen',
            field=models.CharField(default='Red', max_length=16, choices=[(b'Red', b'Red'), (b'Yellow', b'Yellow'), (b'Green', b'Green')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studygroupmeeting',
            name='meeting_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 29, 0, 50, 5, 626746, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
