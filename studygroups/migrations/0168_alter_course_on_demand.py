# Generated by Django 3.2.13 on 2022-09-20 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0167_auto_20220919_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='on_demand',
            field=models.BooleanField(default=False),
        ),
    ]