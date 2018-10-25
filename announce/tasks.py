from celery import shared_task

from django.contrib.auth.models import User
#TODO from custom_registration.models import Profile


@shared_task
def send_announcement(sender, subject, body_text, body_html):
    print(sender)
    print(subject)
    print(body_text)
    print(body_html)
