# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='name',
            field=models.CharField(max_length=128, blank=True)
        ),
    ]
