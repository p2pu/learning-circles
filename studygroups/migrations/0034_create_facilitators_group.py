# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_facilitators_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    group = Group(name="facilitators")
    group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0033_auto_20150826_1408'),
    ]

    operations = [
        migrations.RunPython(create_facilitators_group),
    ]
