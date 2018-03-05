# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0044_auto_20151218_0455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studygroup',
            name='description',
        ),
        migrations.RemoveField(
            model_name='studygroup',
            name='max_size',
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='duration',
            field=models.IntegerField(help_text=b'Meeting duration in minutes.'),
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='location_details',
            field=models.CharField(help_text=b'Meeting room or office number.', max_length=128),
        ),
    ]
