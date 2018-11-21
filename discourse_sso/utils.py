from django.conf import settings
import requests


def discourse_auth():
    return {
        'api_key': settings.DISCOURSE_API_KEY,
        'api_username': settings.DISCOURSE_API_USERNAME
    }


def get_discourse_user_id(user):
    """ Get discourse id for a django.contrib.auth.models.User """
    user_url = '{0}/u/by-external/{1}.json'.format(settings.DISCOURSE_BASE_URL, user.id)
    resp = requests.get(user_url, params=discourse_auth())
    return resp.json().get('user',{}).get('id')


def anonymize_discourse_user(user):
    """ Anonymize user on discourse if they exist, returns whether a user was deleted """
    discourse_user_id = get_discourse_user_id(user)
    if discourse_user_id == None:
        return False

    url = '{0}/admin/users/{1}/anonymize'.format(settings.DISCOURSE_BASE_URL, discourse_user_id)
    resp = requests.put(url, data=discourse_auth())
    return resp.status_code == 200
