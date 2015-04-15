# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import s3direct.fields


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0007_auto_20150415_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=s3direct.fields.S3DirectField(blank=True),
        ),
    ]
