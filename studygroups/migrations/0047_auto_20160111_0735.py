# -*- coding: utf-8 -*-


from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0046_auto_20160108_0511'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='studygroup',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 11, 13, 35, 21, 421885, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='location',
            name='contact',
            field=models.CharField(help_text=b'Email or phone for the contact person.', max_length=256),
        ),
    ]
