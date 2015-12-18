# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0043_auto_20151218_0422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(help_text=b'Street address of the location.', max_length=256),
        ),
        migrations.AlterField(
            model_name='location',
            name='contact',
            field=models.CharField(help_text=b'Email of phone for the contact person.', max_length=256),
        ),
        migrations.AlterField(
            model_name='location',
            name='contact_name',
            field=models.CharField(help_text=b'Person that can be contacted at the location.', max_length=256),
        ),
        migrations.AlterField(
            model_name='location',
            name='link',
            field=models.URLField(help_text=b'URL where more info about the location can be seen.', blank=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(help_text=b'Common name used to refer to the location.', max_length=256),
        ),
    ]
