from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail


import random
import string

from studygroups.models import Facilitator

def create_user(email, first_name, last_name, password, mailing_list_signup):
    """ Create a new user using the email as the username  """

    if password == None:
        password = "".join([random.choice(string.letters) for i in range(64)])

    user = User.objects.create_user(
        email.lower(), #use lowercase email as username
        email, #keep email in original case supplied
        password
    )
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    facilitator = Facilitator(user=user) 
    facilitator.mailing_list_signup = mailing_list_signup
    facilitator.save()
    return user


class EmailConfirmTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Remove last login timestamp from hash and replace with date
        # that email address was confirmed 
        confirm_timestamp = '' if user.facilitator.email_confirmed_at is None else user.facilitator.email_confirmed_at.replace(microsecond=0, tzinfo=None)
        return (
            six.text_type(user.pk) + user.password + six.text_type(timestamp) +
            six.text_type(confirm_timestamp)
        )
 

def generate_user_token(user):
    """ generate token for user to validate user email address """
    return EmailConfirmTokenGenerator().make_token(user)
        

def check_user_token(user, token):
    return EmailConfirmTokenGenerator().check_token(user, token)


def confirm_user_email(user):
    user.facilitator.email_confirmed_at = timezone.now()
    user.facilitator.save()


def send_email_confirm_email(user):
    context = {
        "user": user,
        "profile": user.facilitator,
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
