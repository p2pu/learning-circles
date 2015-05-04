# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0015_auto_20150430_0126'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='study_group',
            field=models.ForeignKey(related_name='study_groups_new', blank=True, to='studygroups.StudyGroup', null=True),
        ),
    ]
