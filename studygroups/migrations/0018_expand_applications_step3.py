# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0017_expand_applications_step2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='study_groups',
        ),
    ]
