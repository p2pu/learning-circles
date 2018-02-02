from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .mailchimp import add_member_to_list
from .models import generate_user_token
from studygroups.models import Facilitator

@receiver(post_save, sender=Facilitator)
def handle_new_facilitator(sender, instance, created, **kwargs):
    if not created:
        return

    facilitator = instance
    user = instance.user

    # TODO - do this async
    # TODO change this to an email confirmation message
    context = {
        "user": user,
        "profile": facilitator,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": generate_user_token(user),
        "protocol": "https",
        "domain": settings.DOMAIN
    }

    subject_template = 'custom_registration/email_confirm-subject.txt'
    email_template = 'custom_registration/email_confirm.txt'
    html_email_template = 'custom_registration/email_confirm.html'

    subject = render_to_string(subject_template, context).strip(' \n')
    text_body = render_to_string(email_template, context)
    html_body = render_to_string(html_email_template, context)

    to = [user.email]
    email = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to,
    )
    email.attach_alternative(html_body, 'text/html')
    email.send()


    # TODO - do this async
    # TODO - does this make sense to do before the email address is verified? 
    # Add facilitator to Mailchimp newsletter
    if facilitator.mailing_list_signup:
        add_member_to_list(facilitator.user)
