# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_facilitators_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="facilitators")


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0033_auto_20150826_1408'),
    ]

    operations = [
        migrations.RunPython(create_facilitators_group),
    ]
