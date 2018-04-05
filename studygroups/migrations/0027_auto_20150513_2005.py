# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0026_auto_20150512_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reminder',
            name='meeting_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
