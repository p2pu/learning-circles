# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0057_auto_20160128_0953'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='contact_method',
        ),
    ]
