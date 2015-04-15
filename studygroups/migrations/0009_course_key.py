# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0008_auto_20150415_1241'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='key',
            field=models.CharField(default=b'NOT SET', max_length=255),
        ),
    ]
