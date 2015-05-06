# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0021_auto_20150506_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='contact_method',
            field=models.CharField(max_length=128, choices=[(b'Email', b'Email'), (b'Text', b'Text')]),
        ),
    ]
