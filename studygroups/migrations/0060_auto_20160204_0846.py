# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0059_auto_20160128_1244'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='application',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 4, 8, 46, 50, 835422, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
