# -*- coding: utf-8 -*-


from django.db import migrations, models
import datetime
from django.utils.timezone import utc


def set_meeting_time(apps, schema_editor):
    StudyGroupMeeting = apps.get_model('studygroups', 'StudyGroupMeeting')
    for meeting in StudyGroupMeeting.objects.all():
        meeting.meeting_time = meeting.study_group.meeting_time
        meeting.save()


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0063_auto_20160309_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroupmeeting',
            name='meeting_time',
            field=models.TimeField(),
        ),
        migrations.RunPython(set_meeting_time),
    ]
