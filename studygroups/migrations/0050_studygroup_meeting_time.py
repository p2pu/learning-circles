# -*- coding: utf-8 -*-


from django.db import migrations, models
import datetime
from django.utils.timezone import utc

def set_meeting_time(apps, schema_editor):
    StudyGroup = apps.get_model("studygroups", "StudyGroup")
    for study_group in StudyGroup.objects.all():
        study_group.meeting_time = study_group.start_date.time()
        study_group.save()


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0049_auto_20160114_0418'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='meeting_time',
            field=models.TimeField(default=datetime.datetime(2016, 1, 15, 12, 58, 0, 0, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.RunPython(set_meeting_time),
    ]
