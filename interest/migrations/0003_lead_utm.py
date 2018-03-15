# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interest', '0002_lead_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='utm',
            field=models.CharField(max_length=1024, null=True, verbose_name=b'Acquisition source', blank=True),
        ),
    ]
