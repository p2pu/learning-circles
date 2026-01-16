import json
import datetime

from django.utils.translation import gettext as _
from django.conf import settings

from django.urls import reverse

from django.utils.text import slugify
from courses import db
from content import models as content_model
#from learn import models as learn_model
from media import models as media_model
#from notifications import models as notification_model

from django.contrib.auth import get_user_model
# from users.models import User #NOTE: don't like this dep

User = get_user_model()


import logging
log = logging.getLogger(__name__)


class ResourceNotFoundException(Exception):
    pass


class ResourceDeletedException(Exception):
    pass


class DataIntegrityException(Exception):
    pass


def course_uri2id(course_uri):
    return course_uri.strip('/').split('/')[-1]


def course_id2uri(course_id):
    return '/uri/course/{0}/'.format(course_id)


def _get_course_db(course_uri):
    course_id = course_uri2id(course_uri)
    try:
        course_db = db.Course.objects.get(id=course_id)
    except:
        raise ResourceNotFoundException
    if course_db.deleted:
        raise ResourceDeletedException
    return course_db


def get_course(course_uri):
    course_db = _get_course_db(course_uri)
    course = {
        "id": course_db.id,
        "uri": "/uri/course/{0}".format(course_db.id),
        "title": course_db.title,
        "hashtag": course_db.short_title,
        "slug": slugify(course_db.title),
        "description": course_db.description,
        "language": course_db.language,
        "date_created": course_db.creation_date,
        "author_uri": course_db.creator_uri,
    }

    if course_db.based_on:
        course['based_on_uri'] = "/uri/course/{0}".format(course_db.based_on.id)

    course["status"] = 'published'
    if course_db.archived:
        course["status"] = 'archived'
    elif course_db.draft:
        course["status"] = 'draft'

    if len(course_db.image_uri) > 0:
        course["image_uri"] = course_db.image_uri

    content = get_course_content(course_uri)
    if len(content) > 0:
        course["about_uri"] = content[0]['uri']
    else:
        log.error("missing about content")
        raise DataIntegrityException

    course["content"] = content[1:]
    return course


def get_courses(title=None, hashtag=None, language=None, organizer_uri=None, draft=None, archived=None):
    results = db.Course.objects
    #NOTE: could also take **kwargs and do results.filter(**kwargs)
    filters = { 'deleted': False }
    if title:
        filters['title'] = title
    if hashtag:
        filters['short_title'] = hashtag
    if language:
        filters['language'] = language
    if organizer_uri:
        filters['creator_uri'] = organizer_uri
    if draft != None:
        filters['draft'] = draft
    if archived != None:
        filters['archived'] = archived
    results = results.filter(**filters)
    return [ get_course(course_id2uri(course_db.id)) for course_db in results ]


def get_user_courses(user_uri):
    """ return courses organized or participated in by an user """
    raise Exception('not implemented')
    #signups = db.CohortSignup.objects.filter(user_uri=user_uri, leave_date__isnull=True, cohort__course__archived=False)
    #courses = []
    #for signup in signups:
    #    try:
    #        course = get_course(course_id2uri(signup.cohort.course.id))
    #    except ResourceDeletedException:
    #        continue
    #    course_data = {
    #        "id": course['id'],
    #        "title": course['title'],
    #        "user_role": signup.role,
    #        "url": reverse("courses_show", kwargs={"course_id": course["id"], "slug": course["slug"]}),
    #    }
    #    if "image_uri" in course:
    #        course_data["image_url"] = media_model.get_image(course['image_uri'])['url']
    #    courses += [course_data]
    #return courses


def create_course(title, hashtag, description, language, organizer_uri, based_on_uri=None):
    course_db = db.Course(
        title=title,
        short_title=hashtag,
        description=description,
        language=language,
        creator_uri=organizer_uri
    )

    if based_on_uri:
        based_on = _get_course_db(based_on_uri)
        course_db.based_on = based_on

    course_db.save()

    about = content_model.create_content(
       **{"title": _("About"), "content": "", "author_uri": organizer_uri}
    )
    add_course_content("/uri/course/{0}".format(course_db.id), about['uri'])
    course = get_course("/uri/course/{0}".format(course_db.id))

    return course


def clone_course(course_uri, organizer_uri):
    original_course = get_course(course_uri)
    new_course = create_course(
        original_course['title'],
        original_course['hashtag'],
        original_course['description'],
        original_course['language'],
        organizer_uri,
        course_uri
    )

    new_about = content_model.clone_content(original_course['about_uri'])
    about_db = db.CourseContent.objects.get(content_uri=new_course['about_uri'])
    about_db.content_uri = new_about['uri']
    about_db.save()

    for content in original_course['content']:
        new_content = content_model.clone_content(content['uri'])
        add_course_content(new_course['uri'], new_content['uri'])

    return get_course(new_course['uri'])


def update_course(course_uri, title=None, hashtag=None, description=None, language=None, image_uri=None):
    # TODO
    course_db = _get_course_db(course_uri)
    if title:
        course_db.title = title
    if hashtag:
        course_db.short_title = hashtag
    if description:
        course_db.description = description
    if language:
        course_db.language = language
    if image_uri:
        course_db.image_uri = image_uri

    course_db.save()

    return get_course(course_uri)


def publish_course(course_uri):
    """ publish the course - also add course to the 'listed' list in the learn index """

    course_db = _get_course_db(course_uri)
    if not (course_db.draft or course_db.archived):
        return get_course(course_uri)

    course_db.draft = False
    course_db.archived = False
    course_db.save()

    course = get_course(course_uri)
    course_url = reverse(
        'courses_slug_redirect',
        kwargs={'course_id': course["id"]}
    )
    return course


def archive_course(course_uri):
    """ mark a course as archived - this will also disable editing of the course """
    course_db = _get_course_db(course_uri)
    if course_db.archived:
        return get_course(course_uri)

    course_db.archived = True
    course_db.save()

    course = get_course(course_uri)
    course_url = reverse(
        'courses_slug_redirect',
        kwargs={'course_id': course["id"]}
    )

    return course


def unpublish_course(course_uri):
    course_db = _get_course_db(course_uri)

    if course_db.draft and not course_db.archived:
        return get_course(course_uri)

    course_db.archived = False
    course_db.draft = True
    course_db.save()

    course = get_course(course_uri)
    course_url = reverse(
        'courses_slug_redirect',
        kwargs={'course_id': course["id"]}
    )

    return course


def delete_spam_course(course_uri):
    """ Delete a course and remove listing from index """
    # TODO - this doesn't do anything special for spam, maybe rename the function
    course_id = course_uri2id(course_uri)
    course_db = db.Course.objects.get(id=course_id)
    course_db.deleted = True
    course_db.save()


def get_course_content(course_uri):
    content = []
    course_id = course_uri2id(course_uri)
    course_db = _get_course_db(course_uri)
    for course_content_db in course_db.content.order_by('index'):
        content_data = content_model.get_content(course_content_db.content_uri)
        content += [{
            "id": content_data["id"],
            "uri": content_data["uri"],
            "title": content_data["title"],
            "index": course_content_db.index,
        }]
    return content


def add_course_content(course_uri, content_uri):
    course_id = course_uri2id(course_uri)
    course_db = _get_course_db(course_uri)
    next_index = 0
    try:
        next_index = db.CourseContent.objects.filter(course = course_db).order_by('-index')[0].index + 1
    except:
        # TODO
        pass
    course_content_db = db.CourseContent(
        course=course_db,
        content_uri=content_uri,
        index=next_index
    )
    course_content_db.save()


def remove_course_content(course_uri, content_uri):
    course_id = course_uri2id(course_uri)
    course_db = _get_course_db(course_uri)
    course_content_db = course_db.content.get(content_uri=content_uri)
    course_content_db.delete()
    for content in course_db.content.filter(index__gt=course_content_db.index):
        content.index = content.index - 1
        content.save()


def reorder_course_content(content_uri, direction):
    course_content_db = None
    try:
        course_content_db = db.CourseContent.objects.get(content_uri=content_uri)
    except:
        raise ResourceNotFoundException
    new_index = course_content_db.index + 1
    if direction == "UP":
        new_index = course_content_db.index - 1
    if new_index < 1:
        return

    try:
        swap_course_content_db = db.CourseContent.objects.get(
            course=course_content_db.course, index=new_index
        )
    except:
        #TODO
        raise Exception("Internal error")

    swap_course_content_db.index = course_content_db.index
    course_content_db.index = new_index
    swap_course_content_db.save()
    course_content_db.save()


def get_course_tags(course_uri):
    course_db = _get_course_db(course_uri)
    tags_db = db.CourseTags.objects.filter(course=course_db)
    return tags_db.values_list('tag', flat=True)


def add_course_tags(course_uri, tags):
    course_db = _get_course_db(course_uri)

    for tag in tags:
        if not db.CourseTags.objects.filter(course=course_db, tag=tag).exists():
            tag_db = db.CourseTags(course=course_db, tag=tag)
            tag_db.save()


def remove_course_tags(course_uri, tags):
    course_db = _get_course_db(course_uri)

    for tag_db in db.CourseTags.objects.filter(course=course_db, tag__in=tags):
        tag_db.delete()


def is_organizer(course_uri, user_uri):
    try:
        course_db = _get_course_db(course_uri)
    except:
        raise ResourceNotFoundException

    return course_db.creator_uri == user_uri
