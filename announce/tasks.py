from celery import shared_task

from django.contrib.auth.models import User
from django.conf import settings

from studygroups.models import Profile

import requests
from requests.auth import HTTPBasicAuth
import json
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_announcement(sender, subject, body_text, body_html):
    """ Send message to all users that opted-in for the community email list """

    # Get list of users who opted-in to communications
    users = User.objects.filter(is_active=True, profile__communication_opt_in=True)
    batch_size = 500
    # send in batches of batch_size
    url = 'https://api.mailgun.net/v3/{}/messages'.format(settings.MAILGUN_DOMAIN)
    auth = HTTPBasicAuth('api', settings.MAILGUN_API_KEY)

    for index in range(0, len(users), batch_size):
        to = users[index:index+500]

        post_data = [
            ('from', sender),
            ('subject', subject),
            ('text', body_text),
            ('html', body_html),
            ('o:tracking', 'yes'),
            ('o:tracking-clicks', 'htmlonly'),
            ('o:tracking-opens', 'yes'),
            ('o:tag', 'announce'),
        ]

        post_data += [ ('to', u.email) for u in to ]
        # Add recipient variables to ensure mailgun sends messages individually and
        # not with everyone in the to field.
        post_data += [ ('recipient-variables', json.dumps({ u.email:{} for u in to })) ]
        resp = requests.post(url, auth=auth, data=post_data)
        if resp.status_code != 200:
            logger.error('Could not send mailgun batch email')

