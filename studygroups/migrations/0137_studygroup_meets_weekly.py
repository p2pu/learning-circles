# Generated by Django 2.2.13 on 2020-10-03 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0136_auto_20200902_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='meets_weekly',
            field=models.BooleanField(default=True),
        ),
    ]
