# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-20 13:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0095_studygroup_facilitator_rating'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Activity',
        ),
    ]