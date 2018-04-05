# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0055_application_signup_questions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='computer_access',
        ),
        migrations.RemoveField(
            model_name='application',
            name='goals',
        ),
        migrations.RemoveField(
            model_name='application',
            name='support',
        ),
    ]
