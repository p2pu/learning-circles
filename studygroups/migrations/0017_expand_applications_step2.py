# -*- coding: utf-8 -*-


from django.db import models, migrations

def expand_application(apps, schema_editor):
    Application = apps.get_model("studygroups", "Application")
    for apl in Application.objects.all():
        apl.study_group = apl.study_groups.all()[0]
        apl.save()
        for study_group in apl.study_groups.all()[1:]:
            apl.pk = None
            apl.study_group = study_group
            apl.save()

class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0016_expand_applications_step1'),
    ]

    operations = [
        migrations.RunPython(expand_application),
    ]
