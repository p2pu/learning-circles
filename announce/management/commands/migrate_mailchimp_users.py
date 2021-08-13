from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from announce.mailchimp import clean_members, list_members
from studygroups.models import Profile

import requests

class Command(BaseCommand):
    help = 'Ensure all learning circles have English country name'

    def handle(self, *args, **options):

        # get all mailchimp users
        # make sure no users with communication_opt_in == False is in mailchimp
        # add all members with communicagtion_opt_in == True to mailchimp

        # Download mailchimp users
        mailchimp_members = list_members()
        filter_subscribed = lambda x: x.get('status') not in ['unsubscribed', 'cleaned']
        mailchimp_members = filter(filter_subscribed, mailchimp_members)
        emails = [member.get('email_address').lower() for member in mailchimp_members]
        # Find intersection of User.objects.all() and mailchimp users
        users = User.objects.all()
        users = list(filter(lambda u: u.email.lower() in emails, users))
        # print(users)
        # Add user to the announce list
        Profile.objects.filter(user__in=users).update(communication_opt_in = True)
        print('{} users will be removed from the mailchimp list'.format(len(users)))
        # Delete users from mailchimp if they have an account 
        clean_members(users)

