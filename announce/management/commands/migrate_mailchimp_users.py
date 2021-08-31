from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from announce.mailchimp import archive_members, list_members, batch_subscribe
from studygroups.models import Profile

import requests

class Command(BaseCommand):
    help = 'Ensure all learning circles have English country name'

    def handle(self, *args, **options):

        # get all mailchimp users
        # Download mailchimp users
        mailchimp_members = list_members()
        filter_subscribed = lambda x: x.get('status') not in ['unsubscribed', 'cleaned']
        mailchimp_members = filter(filter_subscribed, mailchimp_members)
        emails = [member.get('email_address').lower() for member in mailchimp_members]

        # make sure no users with communication_opt_in == False is in mailchimp
        unsubscribed_users = User.objects.filter(profile__communication_opt_in=False, is_active=True)
        to_unsub = list(filter(lambda u: u.email.lower() in emails, unsubscribed_users))
        print('{} users will be removed from the mailchimp list'.format(len(to_unsub)))
        archive_members(to_unsub)

        # add all members with communicagtion_opt_in == True to mailchimp
        subscribed = User.objects.filter(profile__communication_opt_in=True, is_active=True)
        to_sub = list(filter(lambda u: u.email.lower() not in emails, subscribed))
        print('{} users will be added to the mailchimp list'.format(len(to_sub)))
        batch_subscribe(to_sub)


