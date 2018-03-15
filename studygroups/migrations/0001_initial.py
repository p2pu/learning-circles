# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('provider', models.CharField(max_length=256)),
                ('link', models.URLField()),
                ('start_date', models.DateField()),
                ('duration', models.CharField(max_length=128)),
                ('prerequisite', models.TextField()),
                ('time_required', models.CharField(max_length=128)),
                ('caption', models.TextField()),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudyGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.CharField(max_length=128)),
                ('location_link', models.URLField()),
                ('time', models.CharField(max_length=128)),
                ('max_size', models.IntegerField()),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(to='studygroups.Course', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudyGroupSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=75)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('study_group', models.ForeignKey(to='studygroups.StudyGroup', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='studygroupsignup',
            unique_together=set([('email', 'study_group')]),
        ),
    ]
