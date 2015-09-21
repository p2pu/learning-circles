# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0039_create_organizers_group_20150918_2046'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='signup_open',
            field=models.BooleanField(default=True),
        ),
    ]
