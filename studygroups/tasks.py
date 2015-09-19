from __future__ import absolute_import

from celery import shared_task

from django.utils import timezone
from django.conf import settings

from studygroups.models import StudyGroup
from studygroups.models import Reminder
from studygroups.models import generate_reminder
from studygroups.models import send_reminder
from studygroups.models import send_weekly_update
from django.utils import translation

import datetime

@shared_task
def send_reminders():
    now = timezone.now()
    translation.activate(settings.LANGUAGE_CODE)
    # TODO - should this be set here or closer to where the language matters?
    for reminder in Reminder.objects.filter(sent_at__isnull=True):
        if reminder.study_group_meeting.meeting_time - now < datetime.timedelta(days=2):
            send_reminder(reminder)


@shared_task
def gen_reminders():
    for study_group in StudyGroup.objects.all():
        translation.activate(settings.LANGUAGE_CODE)
        generate_reminder(study_group)


@shared_task
def weekly_update():
    # Create a report for the previous week
    send_weekly_update()
