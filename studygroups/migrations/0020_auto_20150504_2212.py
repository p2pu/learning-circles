# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0019_auto_20150504_1801'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studygroupsignup',
            name='study_group',
        ),
        migrations.DeleteModel(
            name='StudyGroupSignup',
        ),
    ]
