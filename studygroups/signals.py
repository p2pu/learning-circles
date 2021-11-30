from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from studygroups.utils import render_to_string_ctx
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
from django.utils import timezone

from studygroups.email_helper import render_html_with_css

from .models import Application
from .models import StudyGroup
from .models import Course
from .models import get_study_group_organizers

from .utils import html_body_to_text
from .utils import use_language

from advice.models import Advice

import pytz

@receiver(post_save, sender=Application)
def handle_new_application(sender, instance, created, **kwargs):
    """ Send welcome message to learner introducing them to their facilitator """
    if not created:
        return

    application = instance

    # get a random piece of advice
    # TODO remove unused advice logic
    advice = None
    if application.study_group.language == 'en':
        advice = Advice.objects.order_by('?').first()

    # activate language and timezone for message reminder
    with use_language(application.study_group.language), timezone.override(pytz.timezone(application.study_group.timezone)):
        # Send welcome message to learner
        learner_signup_subject = render_to_string_ctx(
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
    }
    subject = render_to_string_ctx('studygroups/email/learning_circle_created-subject.txt', context).strip(' \n')
    html_body = render_html_with_css('studygroups/email/learning_circle_created.html', context)
    text_body = html_body_to_text(html_body)

    # on all learning circles, CC p2pu
    cc = [settings.TEAM_EMAIL]
    # if the user is part of a team, send to the organizer(s)
    cc += [ o.email for o in get_study_group_organizers(study_group)]
    # if there is a question, send to the welcoming comitte
    if study_group.facilitator_concerns:
        cc += [settings.COMMUNITY_MANAGER]

    notification = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [study_group.facilitator.email],
        cc=cc,
        reply_to=[study_group.facilitator.email] + cc
    )
    notification.attach_alternative(html_body, 'text/html')
    notification.send()
