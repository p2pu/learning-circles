from django.utils import timezone
from django.conf import settings

from studygroups.models import StudyGroup
from studygroups.models import Reminder
from studygroups.models import generate_reminder
from studygroups.models import send_reminder
from django.utils import translation

import datetime

def send_reminders():
    now = timezone.now()
    translation.activate(settings.LANGUAGE_CODE)
    for reminder in Reminder.objects.filter(sent_at__isnull=True):
        if reminder.study_group_meeting.meeting_time - now < datetime.timedelta(days=2):
            send_reminder(reminder)


def gen_reminders():
    for study_group in StudyGroup.objects.all():
        translation.activate(settings.LANGUAGE_CODE)
        generate_reminder(study_group)
