# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def set_venue_info(apps, schema_editor):
    StudyGroup = apps.get_model("studygroups", "StudyGroup")
    for sg in StudyGroup.objects.all():
        sg.venue_name = sg.location.name
        sg.venue_address = sg.location.address
        sg.venue_details = sg.location_details
        sg.venue_website = sg.location.link
        sg.image = sg.location.image
        sg.save()


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0052_course_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='image',
            field=models.ImageField(help_text=b'Make your Circle stand out with a picture. It could be related to location, subject matter, or anything else you want to identify your Circle with.', upload_to=b'', blank=True),
        ),
        migrations.AddField(
            model_name='studygroup',
            name='venue_address',
            field=models.CharField(default='todo', help_text=b'Like you were mailing a letter. Include country!.', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studygroup',
            name='venue_details',
            field=models.CharField(default='todo', help_text=b'e.g. second floor meeting room or kitchen.', max_length=128, verbose_name=b'Meeting spot'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studygroup',
            name='venue_name',
            field=models.CharField(default='todo', help_text=b"e.g. Pretoria Library or Bekka's house", max_length=256, verbose_name=b'Common name of venue.'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studygroup',
            name='venue_website',
            field=models.URLField(help_text=b'Link to any website that has more info about the venue or Circle.', blank=True),
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='course',
            field=models.ForeignKey(help_text=b'Choose one or add a new course.', to='studygroups.Course'),
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='duration',
            field=models.IntegerField(default=90, help_text=b'We recommend 90 minutes - 2 hours.', verbose_name=b'Length of each Circle'),
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='signup_open',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='start_date',
            field=models.DateField(help_text=b'Give yourself at least 4 weeks to market, if possible.', verbose_name=b'First meeting date'),
        ),
        migrations.RunPython(set_venue_info),
    ]
