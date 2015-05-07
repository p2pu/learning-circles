from django.utils import timezone

from studygroups.models import Reminder
from studygroups.models import send_group_message

import datetime

def send_reminders():
    now = timezone.now()
    for reminder in Reminder.objects.filter(sent_at__isnull=True):
        if reminder.meeting_date - now < datetime.timedelta(days=2):
            send_group_message(
                reminder.study_group,
                reminder.email_subject,
                reminder.email_body,
                reminder.sms_body
            )
            reminder.sent_at = now
            reminder.save()
