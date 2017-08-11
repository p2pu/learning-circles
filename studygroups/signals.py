from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings

from models import Application

@receiver(post_save, sender=Application)
def handle_new_application(sender, instance, created, **kwargs):
    if not created:
        return

    application = instance

    # Send notification
    notification_subject = render_to_string(
        'studygroups/email/application-subject.txt',
        {'application': application}
    ).strip('\n')
    notification_body = render_to_string(
        'studygroups/email/application.txt', 
        {'application': application}
    )
    notification_html = render_to_string(
        'studygroups/email/application.html', 
        {'application': application}
    )
    to = [application.study_group.facilitator.email]
    notification = EmailMultiAlternatives(
        notification_subject,
        notification_body,
        settings.SERVER_EMAIL,
        to
    )
    notification.attach_alternative(notification_html, 'text/html')
    notification.send()

