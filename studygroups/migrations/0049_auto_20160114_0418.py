# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0048_auto_20160112_0807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='signup_open',
            field=models.BooleanField(default=False),
        ),
    ]
