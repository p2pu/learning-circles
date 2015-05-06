# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def update_contact_method(apps, schema_editor):
    Application = apps.get_model('studygroups', 'Application')
    for apl in Application.objects.all():
        if apl.contact_method == 'Phone':
            apl.contact_method = 'Text'
            apl.save()


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0020_auto_20150504_2212'),
    ]

    operations = [
        migrations.RunPython(update_contact_method),
    ]
