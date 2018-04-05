# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0013_auto_20150420_2108'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='accepted_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
