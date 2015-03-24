# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import studygroups.models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0002_studygroup_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='name',
            field=models.CharField(default=studygroups.models._study_group_name, max_length=128),
            preserve_default=True,
        ),
    ]
