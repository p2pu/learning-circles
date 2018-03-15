# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0012_studygroupsignup_contact_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroupsignup',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
