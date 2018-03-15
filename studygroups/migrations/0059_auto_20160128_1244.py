# -*- coding: utf-8 -*-


from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0058_remove_application_contact_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 28, 12, 43, 51, 548096, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 28, 12, 44, 3, 377732, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studygroupmeeting',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 28, 12, 44, 12, 455435, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studygroupmeeting',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='studygroupmeeting',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 28, 12, 44, 22, 221672, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
