# Generated by Django 3.2.13 on 2022-09-19 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0166_auto_20220914_0901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='resource_format',
            field=models.CharField(choices=[('course', 'Online Course'), ('book', 'Book'), ('video', 'Video'), ('article', 'Article'), ('group', 'Interest Group'), ('other', 'Other')], max_length=128),
        ),
        migrations.AlterField(
            model_name='course',
            name='topic_guides',
            field=models.ManyToManyField(blank=True, null=True, to='studygroups.TopicGuide'),
        ),
        migrations.AlterField(
            model_name='course',
            name='topics',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
