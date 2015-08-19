# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0022_remove_contact_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studygroup',
            name='time',
        ),
        migrations.AddField(
            model_name='studygroup',
            name='time',
            field=models.TimeField(),
        ),
    ]
