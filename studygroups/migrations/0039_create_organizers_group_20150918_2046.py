# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def create_organizers_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="organizers")


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0038_activity'),
    ]

    operations = [
        migrations.RunPython(create_organizers_group),
    ]
