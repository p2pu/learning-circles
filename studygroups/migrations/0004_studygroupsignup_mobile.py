# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0003_auto_20150324_0450'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroupsignup',
            name='mobile',
            field=models.CharField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
    ]
