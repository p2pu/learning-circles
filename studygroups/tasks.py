from django.utils import timezone

from studygroups.models import StudyGroup
from studygroups.models import Reminder
from studygroups.models import generate_reminder
from studygroups.models import send_reminder

import datetime

def send_reminders():
    now = timezone.now()
    for reminder in Reminder.objects.filter(sent_at__isnull=True):
        if reminder.meeting_time - now < datetime.timedelta(days=2):
            send_reminder(reminder)


def gen_reminders():
    for study_group in StudyGroup.objects.all():
        generate_reminder(study_group)
