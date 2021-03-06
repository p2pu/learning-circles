# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-07-16 10:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    replaces = [('studygroups', '0115_team_created_at'), ('studygroups', '0118_teammembership_created_at'), ('studygroups', '0119_team_email_domain'), ('studygroups', '0120_auto_20190618_1937'), ('studygroups', '0121_auto_20190708_2246'), ('studygroups', '0122_auto_20190710_0605'), ('studygroups', '0123_auto_20190715_1242')]

    dependencies = [
        ('studygroups', '0114_auto_20190602_0201'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teammembership',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='email_domain',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='profile',
            name='city',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='profile',
            name='contact_url',
            field=models.URLField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='profile',
            name='country',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='profile',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='place_id',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='profile',
            name='region',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='team',
            name='invitation_token',
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='teammembership',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teammembership',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='teammembership',
            name='weekly_update_opt_in',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='teammembership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
