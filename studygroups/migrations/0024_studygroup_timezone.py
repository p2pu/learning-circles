# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0023_auto_20150506_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='timezone',
            field=models.CharField(default=b'US/Central', max_length=128),
            preserve_default=False,
        ),
    ]
