# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0027_auto_20150513_2005'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('address', models.CharField(max_length=256)),
                ('contact_name', models.CharField(max_length=256)),
                ('contact', models.CharField(max_length=256)),
                ('link', models.URLField()),
            ],
        ),
        migrations.RemoveField(
            model_name='studygroup',
            name='location_link',
        ),
        migrations.AddField(
            model_name='studygroup',
            name='location_details',
            field=models.CharField(default='none', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='location',
            field=models.ForeignKey(to='studygroups.Location'),
        ),
    ]
