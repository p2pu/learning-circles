# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0018_expand_applications_step3'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='study_group',
            field=models.ForeignKey(to='studygroups.StudyGroup'),
        ),
    ]
