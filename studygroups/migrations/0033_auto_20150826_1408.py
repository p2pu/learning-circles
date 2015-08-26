# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0032_auto_20150824_2110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reminder',
            name='meeting_time',
        ),
        migrations.AddField(
            model_name='reminder',
            name='study_group_meeting',
            field=models.ForeignKey(blank=True, to='studygroups.StudyGroupMeeting', null=True),
        ),
    ]
