# Generated by Django 2.2.24 on 2021-12-09 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0154_studygroup_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='unlisted',
            field=models.BooleanField(default=False),
        ),
    ]
