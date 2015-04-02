# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import s3direct.fields


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0004_studygroupsignup_mobile'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='image',
            field=s3direct.fields.S3DirectField(default=' '),
            preserve_default=False,
        ),
    ]
