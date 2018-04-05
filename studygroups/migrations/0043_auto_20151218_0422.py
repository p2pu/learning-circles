# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0042_facilitator_group_to_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='description',
        ),
        migrations.RemoveField(
            model_name='course',
            name='image',
        ),
        migrations.AlterField(
            model_name='course',
            name='caption',
            field=models.TextField(help_text=b'Short description of the course.'),
        ),
        migrations.RemoveField(
            model_name='course',
            name='duration',
        ),
        migrations.AddField(
            model_name='course',
            name='duration',
            field=models.IntegerField(default=6, help_text=b'Number of weeks.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='course',
            name='link',
            field=models.URLField(help_text=b'URL where the course can be accessed.'),
        ),
        migrations.AlterField(
            model_name='course',
            name='prerequisite',
            field=models.TextField(blank=True),
        ),
        migrations.RemoveField(
            model_name='course',
            name='time_required',
        ),
        migrations.AddField(
            model_name='course',
            name='time_required',
            field=models.IntegerField(default=3, help_text=b'Number of hours per week.'),
            preserve_default=False,
        ),
    ]
