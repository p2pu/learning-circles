# Generated by Django 3.2.13 on 2022-08-03 09:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0164_facilitator_data_migration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studygroup',
            old_name='facilitator',
            new_name='created_by',
        ),
    ]
