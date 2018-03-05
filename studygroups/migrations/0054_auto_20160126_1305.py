# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0053_auto_20160126_1158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studygroup',
            name='location',
        ),
        migrations.RemoveField(
            model_name='studygroup',
            name='location_details',
        ),
    ]
