# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0007_auto_20150415_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
