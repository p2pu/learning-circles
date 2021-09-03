from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from announce.mailchimp import archive_members, list_members, batch_subscribe
from studygroups.models import Profile

import requests
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Synchronize mailchimp audience with users that opted in for communications'

    def handle(self, *args, **options):
        # get all mailchimp users
        mailchimp_members = list_members()
        filter_subscribed = lambda x: x.get('status') not in ['unsubscribed', 'cleaned']
        mailchimp_members = filter(filter_subscribed, mailchimp_members)
        emails = [member.get('email_address').lower() for member in mailchimp_members]

        # add all members with communicagtion_opt_in == True to mailchimp
        subscribed = User.objects.filter(profile__communication_opt_in=True, is_active=True, profile__email_confirmed_at__isnull=False)
        to_sub = list(filter(lambda u: u.email.lower() not in emails, subscribed))
        print('{} users will be added to the mailchimp list'.format(len(to_sub)))
        batch_subscribe(to_sub)

        # update profile.communication_opt_in = True for users subscribed to the mailchimp newsletter
        unsubscribed_users = User.objects.filter(profile__communication_opt_in=False, is_active=True, profile__email_confirmed_at__isnull=False)
        to_update = list(filter(lambda u: u.email.lower() in emails, unsubscribed_users))
        for user in to_update:
            user.profile.communication_opt_in = True
            user.profile.save()



