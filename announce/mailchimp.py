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
    # PUT /lists/{list_id}/members/{subscriber_hash}
    api_url = '{0}lists/{1}/members/{2}'.format(
        settings.MAILCHIMP_API_ROOT,
        settings.MAILCHIMP_LIST_ID,
        hashlib.md5(user.email.lower().encode()).hexdigest()
    )

    data = {
        'email_address': user.email,
        'status_if_new': 'subscribed',
        'status': 'subscribed',
        'timestamp_signup': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        "merge_fields": {
            "FNAME": user.first_name,
            "LNAME": user.last_name,
        },
    }

    response = requests.put(
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


def delete_member(email):
    # NOTE: Only do this for deleted accounts!!
    # POST /lists/{list_id}/members/{subscriber_hash}/actions/delete-permanent
    api_url = '{0}/lists/{1}/members/{2}/actions/delete-permanent'.format(
        settings.MAILCHIMP_API_ROOT,
        settings.MAILCHIMP_LIST_ID,
        hashlib.md5(email.lower().encode()).hexdigest()
    )
    response = requests.post(
        api_url, 
        auth=('apikey', settings.MAILCHIMP_API_KEY),
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


def archive_member(user):
    # DELETE /lists/{list_id}/members/{subscriber_hash}
    api_url = '{0}/lists/{1}/members/{2}'.format(
        settings.MAILCHIMP_API_ROOT,
        settings.MAILCHIMP_LIST_ID,
        hashlib.md5(user.email.lower().encode()).hexdigest()
    )
    response = requests.delete(
        api_url, 
        auth=('apikey', settings.MAILCHIMP_API_KEY),
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


def archive_members(users):
    # TODO this will fail above a certain count of users
    # DELETE /lists/<list-id>/members/<email-md5>
    
    print(len(users))
    make_operation = lambda user: {
        "method": "DELETE",
        "path": "/lists/{0}/members/{1}".format(
            settings.MAILCHIMP_LIST_ID,
            hashlib.md5(user.email.lower().encode()).hexdigest()
        ),
        #"body": '{"status": "cleaned"}'
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
            "members": list(map(member_json, users[index:index+500])),
            "update_existing": True,
        }
        try:
            response = requests.post(
                api_url, 
                auth=('apikey', settings.MAILCHIMP_API_KEY),
                json=body
            )
            if response.json().get('errors'):
                logger.warn(
                    'error batch subscribing{}'.format(json.dumps(response.json()['errors'], indent=4))
                )

        except requests.exceptions.HTTPError as err:
            logger.error("Error: {} {}".format(str(response.status_code), err))
            logger.error(json.dumps(response.json(), indent=4))
