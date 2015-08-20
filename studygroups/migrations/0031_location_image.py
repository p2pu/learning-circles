# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0030_auto_20150817_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='image',
            field=models.ImageField(upload_to=b'', blank=True),
        ),
    ]
