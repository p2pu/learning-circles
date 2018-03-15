# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0037_auto_20150908_2246'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=256)),
                ('index', models.PositiveIntegerField(help_text=b'meeting index this activity corresponds to')),
                ('card', models.FileField(upload_to=b'')),
            ],
        ),
    ]
