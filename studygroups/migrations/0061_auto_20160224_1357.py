# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0060_auto_20160204_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='city',
            field=models.CharField(max_length=256, blank=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='duration',
            field=models.IntegerField(help_text=b'Check the course website, or approximate.', verbose_name=b'Number of weeks'),
        ),
        migrations.AlterField(
            model_name='course',
            name='link',
            field=models.URLField(help_text=b'Paste full URL above.', verbose_name=b'Course website'),
        ),
        migrations.AlterField(
            model_name='course',
            name='prerequisite',
            field=models.TextField(help_text=b'e.g. high school diploma or equivalent, pre-calculus, HTML/CSS.', blank=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='provider',
            field=models.CharField(help_text=b'e.g. Khan Academy, edX, Coursera.', max_length=256, verbose_name=b'Course provider'),
        ),
        migrations.AlterField(
            model_name='course',
            name='start_date',
            field=models.DateField(help_text=b"If the course is always available (many are), choose today's date. Note that this is the start date for the course - not for your specific learning circle.", verbose_name=b'Course start date'),
        ),
        migrations.AlterField(
            model_name='course',
            name='time_required',
            field=models.IntegerField(help_text=b'Check the course website, or approximate.', verbose_name=b'Hours per week'),
        ),
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.CharField(max_length=128, verbose_name=b'Course title'),
        ),
        migrations.AlterField(
            model_name='reminder',
            name='sms_body',
            field=models.CharField(max_length=160, verbose_name='SMS (Text)'),
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='venue_address',
            field=models.CharField(help_text=b'Like you were mailing a letter. Include country!', max_length=256),
        ),
    ]
