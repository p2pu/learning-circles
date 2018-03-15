# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('studygroups', '0028_auto_20150806_0039'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='facilitator',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]
