# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0047_auto_20160111_0735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='duration',
            field=models.IntegerField(default=90, help_text=b'Meeting duration in minutes.'),
        ),
    ]
