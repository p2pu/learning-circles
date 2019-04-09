# -*- coding: utf-8 -*-


from django.db import models, migrations
import studygroups.models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0002_studygroup_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='name',
            field=models.CharField(default=studygroups.models.learningcircle._study_group_name, max_length=128),
            preserve_default=True,
        ),
    ]
