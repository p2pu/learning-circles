# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0035_auto_20150828_1950'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='redyellowgreen',
        ),
        migrations.AddField(
            model_name='feedback',
            name='rating',
            field=models.CharField(default='1', max_length=16, choices=[(b'5', b'Great'), (b'4', b'Pretty well'), (b'3', b'Good'), (b'2', b'Not so great'), (b'1', b'I need some help')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='reflection',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='feedback',
            name='feedback',
            field=models.TextField(),
        ),
    ]
