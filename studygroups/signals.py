from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from studygroups.email_helper import render_html_with_css

from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
from django.utils import timezone

from .models import Application
from .models import StudyGroup
from .models import Course

from .utils import html_body_to_text

from advice.models import Advice

import pytz

@receiver(post_save, sender=Application)
def handle_new_application(sender, instance, created, **kwargs):
    """ Send welcome message to learner introducing them to their facilitator """
    if not created:
        return

    application = instance

    # get a random piece of advice
    advice = Advice.objects.order_by('?').first()

    # activitate timezone for message reminder
    with timezone.override(pytz.timezone(application.study_group.timezone)):
        # Send welcome message to learner
        learner_signup_subject = render_to_string(
            'studygroups/email/learner_signup-subject.txt', {
                'application': application,
                'advice': advice,
            }
        ).strip('\n')

        learner_signup_html = render_html_with_css(
            'studygroups/email/learner_signup.html', {
                'application': application,
                'advice': advice,
            }
        )
        learner_signup_body = html_body_to_text(learner_signup_html)

    to = [application.email]
    # CC facilitator and put in reply-to
    welcome_message = EmailMultiAlternatives(
        learner_signup_subject,
        learner_signup_body,
        settings.DEFAULT_FROM_EMAIL,
        to,
        cc=[application.study_group.facilitator.email],
        reply_to=[application.study_group.facilitator.email]
    )
    welcome_message.attach_alternative(learner_signup_html, 'text/html')
    welcome_message.send()


@receiver(post_save, sender=StudyGroup)
def handle_new_study_group_creation(sender, instance, created, **kwargs):
    if not created:
        return

    study_group = instance
    context = {
        'study_group': study_group,
        'protocol': 'https',
        'domain': settings.DOMAIN,
    }
    subject = render_to_string('studygroups/email/learning_circle_created-subject.txt', context).strip(' \n')
    html_body = render_html_with_css('studygroups/email/learning_circle_created.html', context)
    text_body = html_body_to_text(html_body)

    notification = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [study_group.facilitator.email],
        cc=[settings.COMMUNITY_MANAGER],
        reply_to=[study_group.facilitator.email, settings.COMMUNITY_MANAGER]
    )
    notification.attach_alternative(html_body, 'text/html')
    notification.send()
