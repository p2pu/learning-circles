# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-10-25 09:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0103_auto_20181012_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='attach_ics',
            field=models.BooleanField(default=True),
        ),
    ]