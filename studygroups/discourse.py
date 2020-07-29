import requests
import re
import logging

from django.conf import settings

from .models import Course

logger = logging.getLogger(__name__)

def _get_auth():
    return {
        'Api-Key': settings.DISCOURSE_BOT_API_KEY,
        'Api-Username': settings.DISCOURSE_BOT_API_USERNAME,
    }


def create_discourse_topic(title, category, raw):
    create_topic_url = f'{settings.DISCOURSE_BASE_URL}/posts.json'

    request_data = {
        'title': title,
        'category': category,
        'raw': raw,
    }

    request_headers = _get_auth()
    request_headers.update({
        'Content-Type': 'multipart/form-data'
    })

    response = requests.post(create_topic_url, data=request_data, headers=request_headers)

    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        logger.error('Request to Discourse API failed with status code {}. Response text: {}'.format(response.status_code, response.text))
        raise


def get_category_topics(category_id, subcategory_id=None):
    request_data = {
        'api_key': settings.DISCOURSE_BOT_API_KEY,
        'api_username': settings.DISCOURSE_BOT_API_USERNAME,
    }
    category_path = str(category_id)
    if subcategory_id:
        category_path += '/{}'.format(subcategory_id)
    url = '{}/c/{}.json'.format(settings.DISCOURSE_BASE_URL, category_path)
    r = requests.get(url, params=request_data)
    return r.json()


def get_course_topics():
    r = get_category_topics(48, 69)
    topics = r.get('topic_list',{}).get('topics')
    is_course_topic = lambda topic: list(filter(lambda p: p.get('user_id') == 2004, topic.get('posters', [])))
    return filter(is_course_topic, topics)


def get_topic(topic_id):
    url = f'{settings.DISCOURSE_BASE_URL}/t/{topic_id}.json'
    r = requests.get(url, headers=_get_auth())
    return r.json()


def get_post(post_id):
    url = f'{settings.DISCOURSE_BASE_URL}/posts/{post_id}.json'
    r = requests.get(url, headers=_get_auth())
    return r.json()


def update_post(post_id, raw):
    url = f'{settings.DISCOURSE_BASE_URL}/posts/{post_id}.json'
    data = _get_auth()
    data["post[raw]"] = raw
    headers = {
        'Content-Type': 'multipart/form-data'
    }
    r = requests.put(url, data=data, headers=headers)
    if r.status_code == requests.codes.ok:
        print(f'updated post {post_id}')
    else:
        print(f'failed ot update {post_id}')
        print(r.status_code)


def remove_empty_discourse_links():
    """ this was used to fix incorrect course URLs"""
    topics = list(get_course_topics())
    courses = Course.objects.exclude(discourse_topic_url='')
    for course in courses:
        print(course.discourse_topic_url)
        topic_id = course.discourse_topic_url.split('/')[-1]
        topic1 = get_topic(topic_id)
        posts = topic1.get('post_stream', {}).get('posts', [])
        if len(posts) == 1:
            post1_id = posts[0].get('id')
            post1 = get_post(post1_id)
            raw = post1.get('raw')
            match = re.search(r"href='https://learningcircles.p2pu.org/([A-Za-z\-]+)/course/(\d+)", raw)
            if match:
                course_id = match.groups()[1]
                print(f'Unsetting discourse link for {course_id}.')
                Course.objects.filter(pk=course_id).update(discourse_topic_url='')
        else:
            print('Topic has more than 1 post')
