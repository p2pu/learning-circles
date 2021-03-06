# Generated by Django 2.2.13 on 2020-07-03 04:44

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0130_auto_20200623_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='intro_text',
            field=tinymce.models.HTMLField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='team',
            name='website',
            field=models.URLField(blank=True, max_length=128),
        ),
    ]
