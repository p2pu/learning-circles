from django.conf import settings
from django.utils import timezone

import requests
import json
import logging

logger = logging.getLogger(__name__)


def add_member_to_list(user):

    api_url = '{0}lists/{1}/members'.format(
        settings.MAILCHIMP_API_ROOT, settings.MAILCHIMP_LIST_ID
    )

    # POST /lists/{list_id}/members
    data = {
        'email_address': user.email,
        'status': 'subscribed',
        'timestamp_signup': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        "merge_fields": {
            "FNAME": user.first_name,
            "LNAME": user.last_name,
        },
    }

    response = requests.post(
        api_url, 
        auth=('apikey', settings.MAILCHIMP_API_KEY),
        json=data
    )

    try:
        response.raise_for_status()
        body = response.json()
    except requests.exceptions.HTTPError as err:
        logger.error("Error: {} {}".format(str(response.status_code), err))
        logger.error(json.dumps(response.json(), indent=4))
    except ValueError:
        logger.error(u"Cannot decode json, got %s" % response.text)
