# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0061_auto_20160224_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='city',
            field=models.CharField(max_length=256),
        ),
    ]
