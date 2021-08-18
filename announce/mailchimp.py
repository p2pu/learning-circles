from django.conf import settings
from django.utils import timezone

import requests
import json
import logging
import hashlib

logger = logging.getLogger(__name__)

def list_members():
    api_url = '{0}lists/{1}/members'.format(
        settings.MAILCHIMP_API_ROOT, settings.MAILCHIMP_LIST_ID
    )
    count = 500
    params = {
        'count': count,
        'sort_field': 'timestamp_signup',
        'sort_dir': 'ASC',
        'fields': 'total_items,members.email_address,members.status'
    }

    response = requests.get(
        api_url, 
        auth=('apikey', settings.MAILCHIMP_API_KEY),
        params=params
    )
    members = response.json().get('members',[])
    total = response.json().get('total_items')

    for offset in range(count, total, count):
        print('Fetching members {} to {}'.format(offset, offset+count))
        params['offset'] = offset
        response = requests.get(
            api_url, 
            auth=('apikey', settings.MAILCHIMP_API_KEY),
            params=params
        )
        members += response.json().get('members',[])
    return members


def add_member(user):
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
        logger.error("Cannot decode json, got %s" % response.text)


def clean_members(users):
    # Update status to 'cleaned'
    # PATCH /3.0/lists/<list-id>/members/<email-md5> {"status": "cleaned"}
    
    print(len(users))
    make_operation = lambda user: {
        "method": "PATCH",
        "path": "/lists/{0}/members/{1}".format(
            settings.MAILCHIMP_LIST_ID,
            hashlib.md5(user.email.lower().encode()).hexdigest()
        ),
        "body": '{"status": "cleaned"}'
    } 
    batch = {
        "operations": [make_operation(user) for user in users]
    }
    from pprint import pprint
    pprint(batch)

    api_url = '{0}batches'.format(settings.MAILCHIMP_API_ROOT)
    response = requests.post(
        api_url, 
        auth=('apikey', settings.MAILCHIMP_API_KEY),
        json=batch
    )

    try:
        response.raise_for_status()
        body = response.json()
        print(body)
    except requests.exceptions.HTTPError as err:
        logger.error("Error: {} {}".format(str(response.status_code), err))
        logger.error(json.dumps(response.json(), indent=4))
    except ValueError:
        logger.error("Cannot decode json, got %s" % response.text)


def batch_subscribe(users):
    member_json = lambda user: { 
        "email_address": user.email,
        "email_type": "html",
        "status": "subscribed",
    }

    # POST /lists/{list_id}
    api_url = '{0}/lists/{1}'.format(
        settings.MAILCHIMP_API_ROOT,
        settings.MAILCHIMP_LIST_ID
    )

    # NOTE: can only add 500 members at a time
    for index in range(0, len(users), 500):
        body = {
            "members": list(map(member_json, users[index:index+500)),
            "update_existing": True,
        }
        response = requests.post(
            api_url, 
            auth=('apikey', settings.MAILCHIMP_API_KEY),
            json=body
        )
    # TODO report error/success
