# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0011_auto_20150415_1738'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroupsignup',
            name='contact_method',
            field=models.CharField(default='Email', max_length=128, choices=[(b'Email', b'Email'), (b'Text', b'Text'), (b'Phone', b'Phone')]),
            preserve_default=False,
        ),
    ]
