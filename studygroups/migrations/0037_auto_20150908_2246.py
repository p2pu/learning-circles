# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0036_auto_20150908_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='attendance',
            field=models.PositiveIntegerField(),
        ),
    ]
