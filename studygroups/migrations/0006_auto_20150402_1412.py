# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0005_course_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=75)),
                ('mobile', models.CharField(max_length=20, null=True, blank=True)),
                ('contact_method', models.CharField(max_length=128, choices=[(b'Email', b'Email'), (b'Text', b'Text'), (b'Phone', b'Phone')])),
                ('computer_access', models.CharField(max_length=128, choices=[(b'Yes', b'Yes'), (b'No', b'No'), (b'Sometimes', b'Sometimes')])),
                ('goals', models.TextField()),
                ('support', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('study_groups', models.ManyToManyField(to='studygroups.StudyGroup')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='studygroup',
            name='day',
            field=models.CharField(default='Monday', max_length=128, choices=[(b'Monday', b'Monday'), (b'Tuesday', b'Tuesday'), (b'Wednesday', b'Wednesday'), (b'Thursday', b'Thursday'), (b'Friday', b'Friday'), (b'Saturday', b'Saturday'), (b'Sunday', b'Sunday')]),
            preserve_default=False,
        ),
    ]
