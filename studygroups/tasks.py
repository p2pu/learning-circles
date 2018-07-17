from celery import shared_task

from django.utils import timezone
from django.conf import settings
from django.utils import translation
from django.contrib.auth.models import User

from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Reminder
from studygroups.models import generate_reminder
from studygroups.models import send_reminder
from studygroups.models import send_weekly_update
from studygroups.models import send_new_studygroup_email
from studygroups.models import send_new_facilitator_email
from studygroups.models import send_survey_reminder
from studygroups.models import send_facilitator_survey
from studygroups.models import send_last_week_group_activity

import datetime


@shared_task
def send_reminders():
    now = timezone.now()
    translation.activate(settings.LANGUAGE_CODE)
    # TODO - should this be set here or closer to where the language matters?
    # make sure both the StudyGroup and Meeting is still available
    reminders = Reminder.objects.filter(
        sent_at__isnull=True,
        study_group__in=StudyGroup.objects.published(),
        study_group_meeting__in=Meeting.objects.active()
    )
    for reminder in reminders:
        # don't send reminders older than the meeting
        meeting_datetime = reminder.study_group_meeting.meeting_datetime()
        if reminder.study_group_meeting and meeting_datetime - now < datetime.timedelta(days=2) and meeting_datetime > now:
            send_reminder(reminder)


@shared_task
def gen_reminders():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        generate_reminder(study_group)


@shared_task
def weekly_update():
    # Create a report for the previous week
    send_weekly_update()


@shared_task
def send_new_facilitator_emails():
    # send email to organizers who signed up a week ago
    now = timezone.now()
    seven_days_ago = now.date() - datetime.timedelta(days=7)
    six_days_ago = now.date() - datetime.timedelta(days=6)
    for facilitator in User.objects.filter(date_joined__gte=seven_days_ago, date_joined__lt=six_days_ago):
        send_new_facilitator_email(facilitator)


@shared_task
def send_new_studygroup_emails():
    # send email to organizers who created a learning circle a week ago
    now = timezone.now()
    seven_days_ago = now.date() - datetime.timedelta(days=7)
    six_days_ago = now.date() - datetime.timedelta(days=6)
    for studygroup in StudyGroup.objects.filter(created_at__gte=seven_days_ago, created_at__lt=six_days_ago):
        send_new_studygroup_email(studygroup)


@shared_task
def send_all_studygroup_survey_reminders():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        send_survey_reminder(study_group)


@shared_task
def send_all_facilitator_surveys():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        send_facilitator_survey(study_group)


@shared_task
def send_all_last_week_group_activities():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        send_last_week_group_activity(study_group)
