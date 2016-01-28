# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0056_auto_20160126_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='email',
            field=models.EmailField(default='', max_length=254, verbose_name=b'Email address', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='application',
            name='mobile',
            field=models.CharField(default='', max_length=20, blank=True),
            preserve_default=False,
        ),
    ]
