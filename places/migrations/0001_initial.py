# Generated by Django 3.2.15 on 2022-11-01 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=256)),
                ('region', models.CharField(blank=True, max_length=256)),
                ('country', models.CharField(blank=True, max_length=256)),
                ('country_en', models.CharField(blank=True, max_length=256)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=8, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('place_id', models.CharField(blank=True, max_length=256)),
                ('geonameid', models.CharField(blank=True, max_length=32)),
            ],
        ),
    ]
