# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0024_studygroup_timezone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('meeting_time', models.DateTimeField()),
                ('email_subject', models.CharField(max_length=256)),
                ('email_body', models.TextField()),
                ('sms_body', models.CharField(max_length=160)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sent_at', models.DateTimeField(null=True, blank=True)),
                ('study_group', models.ForeignKey(to='studygroups.StudyGroup', on_delete=models.CASCADE)),
            ],
        ),
    ]
