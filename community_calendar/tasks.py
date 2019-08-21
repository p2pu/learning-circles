from celery import shared_task

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives

from studygroups.utils import html_body_to_text
from studygroups.utils import render_to_string_ctx

import logging


logger = logging.getLogger(__name__)


@shared_task
def send_new_event_notification(event):
    to = User.objects.filter(is_staff=True).values_list('email', flat=True)
    context = {
        "event": event
    }

    subject = render_to_string_ctx('community_calendar/new_event-subject.txt', context).strip('\n')
    html_body = render_to_string_ctx('community_calendar/new_event.html', context)
    text_body = html_body_to_text(html_body)

    notification = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        bcc=to
    )
    notification.attach_alternative(html_body, 'text/html')
    try:
        notification.send()
    except Exception as e:
        logger.exception('Could not sent event notification', exc_info=e)
