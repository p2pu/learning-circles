from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from studygroups.utils import render_to_string_ctx
from studygroups.email_helper import render_html_with_css
from django.core.mail import EmailMultiAlternatives, send_mail


import random
import string
import re

from studygroups.models import Profile
from studygroups.models import Team
from studygroups.models import TeamInvitation
from studygroups.models import TeamMembership
from studygroups.utils import html_body_to_text

def create_user(email, first_name, last_name, password, communication_opt_in=False, interested_in_learning=''):
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

    profile = Profile(user=user)
    profile.communication_opt_in = communication_opt_in
    profile.interested_in_learning = interested_in_learning
    profile.save()
    return user


class EmailConfirmTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Remove last login timestamp from hash and replace with date
        # that email address was confirmed
        confirm_timestamp = '' if user.profile.email_confirmed_at is None else user.profile.email_confirmed_at.replace(microsecond=0, tzinfo=None)
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
    user.profile.email_confirmed_at = timezone.now()
    user.profile.save()


def send_email_confirm_email(user):
    context = {
        "user": user,
        "profile": user.profile,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": generate_user_token(user),
    }

    subject_template = 'custom_registration/email_confirm-subject.txt'
    email_template = 'custom_registration/email_confirm.txt'
    html_email_template = 'custom_registration/email_confirm.html'

    subject = render_to_string_ctx(subject_template, context).strip(' \n')
    text_body = render_to_string_ctx(email_template, context)
    html_body = render_html_with_css(html_email_template, context)

    to = [user.email]
    email = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to,
    )
    email.attach_alternative(html_body, 'text/html')
    email.send()


def send_new_user_email(user):
    context = {
        "user": user,
    }

    subject_template = 'custom_registration/new_user_confirmed-subject.txt'
    html_email_template = 'custom_registration/new_user_confirmed.html'

    subject = render_to_string_ctx(subject_template, context).strip(' \n')
    html_body = render_html_with_css(html_email_template, context)
    text_body = html_body_to_text(html_body)

    to = [user.email]
    email = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to,
    )
    email.attach_alternative(html_body, 'text/html')
    email.send()


def eligible_team_by_email_domain(user):
    # user is already on a team
    if TeamMembership.objects.filter(user=user).exists():
        return None

    email_domain = user.email.rsplit('@', 1)[1]
    matching_team = Team.objects.filter(email_domain=email_domain).first()

    # user already has an explicit invitation to this team or has already responsed to an invitation to this team
    if TeamInvitation.objects.filter(email=user.emailgi, team=matching_team).exists():
        return None

    # team must have an organizer to create invitation
    if not TeamMembership.objects.filter(team=matching_team, role=TeamMembership.ORGANIZER).exists():
        return None

    return matching_team

