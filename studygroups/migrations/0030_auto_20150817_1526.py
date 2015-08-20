# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0029_studygroup_facilitator'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feedback', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Rsvp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attending', models.BooleanField()),
                ('application', models.ForeignKey(to='studygroups.Application')),
            ],
        ),
        migrations.CreateModel(
            name='StudyGroupMeeting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meeting_time', models.DateTimeField(null=True, blank=True)),
                ('study_group', models.ForeignKey(to='studygroups.StudyGroup')),
            ],
        ),
        migrations.AddField(
            model_name='rsvp',
            name='study_group_meeting',
            field=models.ForeignKey(to='studygroups.StudyGroupMeeting'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='study_group_meeting',
            field=models.ForeignKey(to='studygroups.StudyGroupMeeting'),
        ),
    ]
