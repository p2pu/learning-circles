# Generated by Django 2.2.24 on 2021-11-29 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0152_application_anonymized'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='membership',
            field=models.BooleanField(default=False),
        ),
    ]
