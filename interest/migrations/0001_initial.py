# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('mobile', models.CharField(max_length=30, null=True, blank=True)),
                ('course', models.CharField(max_length=1024, null=True, blank=True)),
                ('location', models.CharField(max_length=1024, null=True, blank=True)),
                ('time', models.CharField(max_length=1024, null=True, blank=True)),
            ],
        ),
    ]
