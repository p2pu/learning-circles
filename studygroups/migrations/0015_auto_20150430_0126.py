# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0014_application_accepted_at'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='studygroupsignup',
            unique_together=set([]),
        ),
    ]
