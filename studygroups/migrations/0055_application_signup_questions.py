# -*- coding: utf-8 -*-


from django.db import migrations, models
import json

def set_signup_questions(apps, schema_editor):
    Application = apps.get_model("studygroups", "Application")
    for apl in Application.objects.all():
        signup_questions = {
            'computer_access': apl.computer_access,
            'goals': apl.goals,
            'support': apl.support,
        }
        apl.signup_questions = json.dumps(signup_questions)
        apl.save()


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0054_auto_20160126_1305'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='signup_questions',
            field=models.TextField(default='{}'),
            preserve_default=False,
        ),
        migrations.RunPython(set_signup_questions),
    ]
