# Generated by Django 2.2.13 on 2020-11-10 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0139_team_subtitle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='subtitle',
            field=models.CharField(default='Join your neighbors to learn something together. Learning circles meet weekly for 6-8 weeks, and are free to join.', max_length=256),
        ),
    ]
