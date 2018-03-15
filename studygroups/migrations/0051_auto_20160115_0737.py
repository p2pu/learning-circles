# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0050_studygroup_meeting_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='start_date',
            field=models.DateField(help_text=b'Date of the first meeting'),
        ),
    ]
