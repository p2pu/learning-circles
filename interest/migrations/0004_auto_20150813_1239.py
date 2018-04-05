# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interest', '0003_lead_utm'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='source',
            field=models.CharField(max_length=1024, null=True, verbose_name=b'Where did you hear about learning circles?', blank=True),
        ),
        migrations.AlterField(
            model_name='lead',
            name='utm',
            field=models.CharField(max_length=1024, null=True, verbose_name=b'UTM tracking data', blank=True),
        ),
    ]
