# -*- coding: utf-8 -*-


from django.db import models, migrations


def convert_from_group_to_models(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Organizer = apps.get_model('studygroups', 'Organizer')
    Facilitator = apps.get_model('studygroups', 'Facilitator')
    organizers = Group.objects.get(name='organizers')
    for organizer in organizers.user_set.all():
        Organizer.objects.create(user=organizer)
    facilitators = Group.objects.get(name='facilitators')
    for facilitator in facilitators.user_set.all():
        Facilitator.objects.create(user=facilitator)


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0041_facilitator_organizer'),
    ]

    operations = [
        migrations.RunPython(convert_from_group_to_models),
    ]
