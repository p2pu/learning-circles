# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0009_course_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='computer_access',
            field=models.CharField(max_length=128, choices=[(b'No', b'No'), (b'Sometimes', b'Sometimes'), (b'Yes', b'Yes')]),
        ),
    ]
