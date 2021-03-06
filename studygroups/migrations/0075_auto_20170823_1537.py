# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-08-23 15:37


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0074_remove_course_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='course',
            name='prerequisite',
        ),
        migrations.RemoveField(
            model_name='course',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='course',
            name='time_required',
        ),
        migrations.AddField(
            model_name='course',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='language',
            field=models.CharField(default='en', max_length=6, verbose_name='Langauge of the course'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='on_demand',
            field=models.BooleanField(default=True, help_text='Can this course be started at any time'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='topics',
            field=models.TextField(default='', help_text='Pick some topics for your course.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='studygroup',
            name='description',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
    ]
