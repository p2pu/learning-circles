from celery import shared_task

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

from studygroups.models import Profile
from .models import send_new_user_email

import datetime


@shared_task
def send_new_user_emails():
    """  send welcome message to users who confirmed their email in the previous 10 minutes """
    now = timezone.now()
    last_10 = now - datetime.timedelta(minutes=now.minute%10, seconds=now.second, microseconds=now.microsecond)
    last_20 = last_10 - datetime.timedelta(minutes=10)
    for profile in Profile.objects.filter(email_confirmed_at__gte=last_20, email_confirmed_at__lt=last_10):
        send_new_user_email(profile.user)



