# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('interest', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 22, 21, 3, 17, 109244, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
