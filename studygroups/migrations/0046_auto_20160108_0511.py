# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0045_auto_20151218_0811'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='image',
            field=models.ImageField(help_text=b"A photo to represent your Learning Circle. It could be a picture of the building, or anything else you'd like to choose!", upload_to=b'', blank=True),
        ),
    ]
