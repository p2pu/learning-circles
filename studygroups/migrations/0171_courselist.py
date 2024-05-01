# Generated by Django 3.2.15 on 2023-09-07 12:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0170_topicguide_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courses', models.ManyToManyField(to='studygroups.Course')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studygroups.team')),
            ],
        ),
    ]