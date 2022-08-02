from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery
from django.contrib.postgres.search import SearchVector
from django.core.files.storage import get_storage_class
from django.db import models
from django.db.models import Q, F, Case, When, Value, Sum, Min, Max, OuterRef, Subquery, Count, CharField
from django.db.models.functions import Length
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import get_language_info
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseForbidden
from django.views.decorators.cache import cache_control

from collections import Counter
import json
import datetime
import re
import pytz
import logging

from studygroups.decorators import user_is_group_facilitator
from studygroups.decorators import user_is_team_organizer
from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Facilitator
from studygroups.models import Application
from studygroups.models import Meeting
from studygroups.models import Reminder
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import Announcement
from studygroups.models import FacilitatorGuide
from studygroups.models import generate_meetings_from_dates
from studygroups.models import get_json_response
from studygroups.models.course import course_platform_from_url
from studygroups.models.team import eligible_team_by_email_domain, get_team_users
from studygroups.models.learningcircle import generate_meeting_reminder
from studygroups.tasks import send_cofacilitator_email
from studygroups.tasks import send_cofacilitator_removed_email

from uxhelpers.utils import json_response

from api.geo import getLatLonDelta
from api import schema
from api.forms import ImageForm

logger = logging.getLogger(__name__)


def studygroups(request):
    # TODO remove this API endpoint, where is it currently being used??
    study_groups = StudyGroup.objects.published().filter(members_only=False)
    if 'course_id' in request.GET:
        study_groups = study_groups.filter(course_id=request.GET.get('course_id'))

    def to_json(sg):
        data = {
            "name": sg.name,
            "course_title": sg.course.title,
            "facilitator": sg.facilitator.first_name + " " + sg.facilitator.last_name,
            "venue": sg.venue_name,
            "venue_address": sg.venue_address + ", " + sg.city,
            "city": sg.city,
            "day": sg.day(),
            "start_date": sg.start_date,
            "meeting_time": sg.meeting_time,
            "time_zone": sg.timezone_display(),
            "end_time": sg.end_time(),
            "weeks": sg.meeting_set.active().count(),
            "url": f"{settings.PROTOCOL}://{settings.DOMAIN}" + reverse('studygroups_signup', args=(slugify(sg.venue_name, allow_unicode=True), sg.id,)),
        }
        if sg.image:
            data["image_url"] = f"{settings.PROTOCOL}://{settings.DOMAIN}" + sg.image.url
        #TODO else set default image URL
        return data

    data = [ to_json(sg) for sg in study_groups ]
    return json_response(request, data)


class CustomSearchQuery(SearchQuery):

    """ NOTE: This is potentially unsafe!!"""
    def __init__(self, value, search_type='raw', **kwargs):
        # update passed in value to support prefix matching
        query = re.sub(r'[!\'()|&\:=,\.\ \-\<\>@]+', ' ', value).strip().lower()
        tsquery = ":* & ".join(query.split(' '))
        tsquery += ":*"
        super().__init__(tsquery, search_type=search_type, **kwargs) 


def serialize_learning_circle(sg):

    facilitators = [f.user.first_name for f in sg.cofacilitators.all()]
    data = {
        "course": {
            "id": sg.course.pk,
            "title": sg.course.title,
            "provider": sg.course.provider,
            "link": sg.course.link,
            "course_page_url": settings.PROTOCOL + '://' + settings.DOMAIN + reverse('studygroups_course_page', args=(sg.course.id,)),
            "discourse_topic_url": sg.course.discourse_topic_url if sg.course.discourse_topic_url else settings.PROTOCOL + '://' + settings.DOMAIN + reverse("studygroups_generate_course_discourse_topic", args=(sg.course.id,)),
        },
        "id": sg.id,
        "name": sg.name,
        "facilitator": sg.facilitators_display(),
        "facilitators": facilitators,
        "venue": sg.venue_name,
        "venue_address": sg.venue_address + ", " + sg.city,
        "venue_website": sg.venue_website,
        "city": sg.city,
        "region": sg.region,
        "country": sg.country,
        "country_en": sg.country_en,
        "latitude": sg.latitude,
        "longitude": sg.longitude,
        "place_id": sg.place_id,
        "online": sg.online,
        "language": sg.language,
        "day": sg.day(),
        "start_date": sg.start_date,
        "start_datetime": sg.local_start_date(),
        "meeting_time": sg.meeting_time,
        "time_zone": sg.timezone_display(),
        "last_meeting_date": sg.end_date, # TODO rename to end_date or last_meeting_date - ie make consistent
        "end_time": sg.end_time(),
        "weeks": sg.weeks if sg.draft else sg.meeting_set.active().count(), # TODO
        "url": f"{settings.PROTOCOL}://{settings.DOMAIN}" + reverse('studygroups_signup', args=(slugify(sg.venue_name, allow_unicode=True), sg.id,)),
        "report_url": sg.report_url(),
        "studygroup_path": reverse('studygroups_view_study_group', args=(sg.id,)),
        "draft": sg.draft,
        "signup_count": sg.application_set.active().count(),
        "signup_open": sg.signup_open and sg.end_date > datetime.date.today(),
    }

    if sg.image:
        data["image_url"] = settings.PROTOCOL + '://' + settings.DOMAIN + sg.image.url
    # TODO else set default image URL
    if sg.signup_question:
        data["signup_question"] = sg.signup_question
    if hasattr(sg, 'next_meeting_date'):
        data["next_meeting_date"] = sg.next_meeting_date
    if hasattr(sg, 'status'):
        data["status"] = sg.status
    return data


def _intCommaList(csv):
    values = csv.split(',') if csv else []
    cleaned = []
    for value in values:
        try:
            v = int(value)
            cleaned += [v]
        except ValueError:
            return None, 'Not a list of integers seperated by commas'
    return cleaned, None


def _limit_offset(request):
    if 'offset' in request.GET or 'limit' in request.GET:
        try:
            offset = int(request.GET.get('offset', 0))
        except ValueError as e:
            offset = 0
        try:
            limit = int(request.GET.get('limit', 100))
        except ValueError as e:
            limit = 100
    return limit, offset


@method_decorator(cache_control(max_age=15*60), name='dispatch')
class LearningCircleListView(View):
    def get(self, request):
        query_schema = {
            "latitude": schema.floating_point(),
            "longitude": schema.floating_point(),
            "distance": schema.floating_point(),
            "offset": schema.integer(),
            "limit": schema.integer(),
            "weekdays": _intCommaList,
            "user": schema.boolean(),
            "scope": schema.text(),
            "draft": schema.boolean(),
            "team_id": schema.integer(),
            "cu_credit": schema.boolean(),
            "online": schema.boolean(),
            "order": lambda v: (v, None) if v in ['name', 'start_date', 'created_at', 'first_meeting_date', 'last_meeting_date', None] else (None, "must be 'name', 'created_at', 'first_meeting_date', 'last_meeting_date', or 'start_date'"),
        }
        data = schema.django_get_to_dict(request.GET)
        clean_data, errors = schema.validate(query_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        study_groups = StudyGroup.objects.published().filter(members_only=False).prefetch_related('course', 'meeting_set', 'application_set', 'cofacilitators', 'cofacilitators__user').order_by('id')

        if 'draft' in request.GET:
            study_groups = StudyGroup.objects.active().order_by('id')
        if 'id' in request.GET:
            id = request.GET.get('id')
            study_groups = StudyGroup.objects.filter(pk=int(id))

        if 'user' in request.GET:
            study_groups = study_groups.filter(cofacilitators__user=request.user)

        if 'online' in request.GET:
            online = clean_data.get('online')
            study_groups = study_groups.filter(online=online)

        if clean_data.get('cu_credit'):
            study_groups = study_groups.filter(cu_credit=True)

        today = datetime.date.today()
        active_meetings = Meeting.objects.filter(study_group=OuterRef('pk'), deleted_at__isnull=True).order_by('meeting_date')
        # TODO status is being used by the learning circle search page?
        study_groups = study_groups.annotate(
            status=Case(
                When(signup_open=True, start_date__gt=today, then=Value('upcoming')),
                When(signup_open=True, start_date__lte=today, end_date__gte=today, then=Value('in_progress')),
                When(signup_open=False, end_date__gte=today, then=Value('closed')),
                default=Value('completed'),
                output_field=CharField(),
            ),
        )

        # TODO scope is used by dashboard?
        if 'scope' in request.GET:
            scope = request.GET.get('scope')
            upcoming_meetings = Meeting.objects.filter(study_group=OuterRef('pk'), deleted_at__isnull=True, meeting_date__gte=today).order_by('meeting_date')

            if scope == "active":
                study_groups = study_groups\
                .annotate(next_meeting_date=Subquery(upcoming_meetings.values('meeting_date')[:1]))\
                .filter(Q(end_date__gte=today) | Q(draft=True))
            elif scope == "upcoming":
                study_groups = study_groups\
                .annotate(next_meeting_date=Subquery(upcoming_meetings.values('meeting_date')[:1]))\
                .filter(Q(start_date__gt=today) | Q(draft=True))
            elif scope == "current":
                study_groups = study_groups\
                .annotate(next_meeting_date=Subquery(upcoming_meetings.values('meeting_date')[:1]))\
                .filter(start_date__lte=today, end_date__gte=today)
            elif scope == "completed":
                study_groups = study_groups\
                .filter(end_date__lt=today)

        q = request.GET.get('q', '').strip()

        if q:
            tsquery = CustomSearchQuery(q, config='simple')
            study_groups = study_groups.annotate(
                search = SearchVector(
                    'city',
                    'name',
                    'course__title',
                    'course__provider',
                    'course__topics',
                    'venue_name',
                    'venue_address',
                    'venue_details',
                    'facilitator__first_name', # TODO - does this need to be cofacilitators__user__first_name?
                    config='simple'
                )
            ).filter(search=tsquery)

        if 'course_id' in request.GET:
            study_groups = study_groups.filter(
                course_id=request.GET.get('course_id')
            )

        city = request.GET.get('city')
        if city is not None:
            study_groups = study_groups.filter(city=city)

        team_id = request.GET.get('team_id')
        if team_id is not None:
            study_groups = study_groups.filter(team_id=team_id)

        # TODO How is this different from scope=active?
        if 'active' in request.GET:
            active = request.GET.get('active') == 'true'
            if active:
                study_groups = study_groups.filter(end_date__gte=today)
            else:
                study_groups = study_groups.filter(end_date__lt=today)

        if 'latitude' in request.GET and 'longitude' in request.GET:
            # work with floats for ease
            latitude = float(request.GET.get('latitude'))
            longitude = float(request.GET.get('longitude'))
            distance = float(request.GET.get('distance', False) or 50)
            lat_delta, lon_delta = getLatLonDelta(latitude, longitude, distance)
            lat_min = max(-90, latitude - lat_delta)
            lat_max = min(90, latitude + lat_delta)
            lon_min = max(-180, longitude - lon_delta)
            lon_max = min(180, longitude + lon_delta)
            # NOTE doesn't wrap around,
            # iow, something at lat=45, lon=-189 and distance=1000 won't match
            # lat=45, lon=189 even though they are only 222 km apart.
            study_groups = study_groups.filter(
                latitude__gte=lat_min,
                latitude__lte=lat_max,
                longitude__gte=lon_min,
                longitude__lte=lon_max
            )
            # NOTE could use haversine approximation to filter more accurately

        if 'topics' in request.GET:
            topics = request.GET.get('topics').split(',')
            query = Q(course__topics__icontains=topics[0])
            for topic in topics[1:]:
                query = Q(course__topics__icontains=topic) | query
            study_groups = study_groups.filter(query)

        if 'weekdays' in request.GET:
            weekdays = request.GET.get('weekdays').split(',')
            query = None
            for weekday in weekdays:
                # __week_day differs from datetime.weekday()
                # Monday should be 0
                weekday = int(weekday) + 2 % 7
                query = query | Q(start_date__week_day=weekday) if query else Q(start_date__week_day=weekday)
            study_groups = study_groups.filter(query)

        # TODO this conflates signup open and active
        study_groups_signup_open = study_groups.filter(signup_open=True, end_date__gte=today)
        study_groups_signup_closed = study_groups.filter(Q(signup_open=False) | Q(end_date__lt=today))

        if 'signup' in request.GET:
            signup_open = request.GET.get('signup') == 'open'
            if signup_open:
                study_groups = study_groups_signup_open
            else:
                study_groups = study_groups_signup_closed

        order = request.GET.get('order', None)
        if order == 'name':
            study_groups = study_groups.order_by('name')
        elif order == 'start_date':
            study_groups = study_groups.order_by('-start_date')
        elif order == 'created_at':
            study_groups = study_groups.order_by('-created_at')
        elif order == 'first_meeting_date':
            study_groups = study_groups.order_by('start_date')
        elif order == 'last_meeting_date':
            study_groups = study_groups.order_by('-end_date')

        data = {
            'count': study_groups.count(),
            'signup_open_count': study_groups_signup_open.count(),
            'signup_closed_count': study_groups_signup_closed.count(),
        }

        if 'offset' in request.GET or 'limit' in request.GET:
            limit, offset = _limit_offset(request)
            data['offset'] = offset
            data['limit'] = limit
            study_groups = study_groups[offset:offset+limit]

        data['items'] = [ serialize_learning_circle(sg) for sg in study_groups ]
        return json_response(request, data)


class LearningCircleTopicListView(View):
    """ Return topics for listed courses """
    def get(self, request):
        study_group_ids = Meeting.objects.active().filter(
            meeting_date__gte=timezone.now()
        ).values('study_group')
        course_ids = None
        course_ids = StudyGroup.objects.published().filter(id__in=study_group_ids).values('course')

        topics = Course.objects.active()\
            .filter(unlisted=False)\
            .filter(id__in=course_ids)\
            .exclude(topics='')\
            .values_list('topics')
        topics = [
            item.strip().lower() for sublist in topics for item in sublist[0].split(',')
        ]
        data = {}
        data['topics'] = { k: v for k, v in list(Counter(topics).items()) }
        return json_response(request, data)


def _studygroup_object_for_map(sg):
    active = sg.end_date > datetime.date.today()
    report_available = sg.learnersurveyresponse_set.count() > 0

    data = {
        "id": sg.id,
        "title": sg.name,
        "latitude": sg.latitude,
        "longitude": sg.longitude,
        "city": sg.city,
        "start_date": sg.start_date,
        "active": active
    }

    if active:
        data["url"] = settings.PROTOCOL + '://' + settings.DOMAIN + reverse('studygroups_signup', args=(slugify(sg.venue_name, allow_unicode=True), sg.id,))
    elif report_available:
        data["report_url"] = sg.report_url()

    return data


class LearningCirclesMapView(View):
    def get(self, request):
        study_groups = StudyGroup.objects.published().select_related('course').prefetch_related("learnersurveyresponse_set")
        data = {}
        data['items'] = [ _studygroup_object_for_map(sg) for sg in study_groups ]
        return json_response(request, data)


def _course_check(course_id):
    if not Course.objects.filter(pk=int(course_id)).exists():
        return None, 'Course matching ID not found'
    else:
        return Course.objects.get(pk=int(course_id)), None


def serialize_course(course):
    data = {
        "id": course.id,
        "title": course.title,
        "provider": course.provider,
        "platform": course.platform,
        "link": course.link,
        "caption": course.caption,
        "on_demand": course.on_demand,
        "topics": [t.strip() for t in course.topics.split(',')] if course.topics else [],
        "language": course.language,
        "overall_rating": course.overall_rating,
        "total_ratings": course.total_ratings,
        "rating_step_counts": course.rating_step_counts,
        "course_page_url": settings.PROTOCOL + '://' + settings.DOMAIN + reverse("studygroups_course_page", args=(course.id,)),
        "course_page_path": reverse("studygroups_course_page", args=(course.id,)),
        "course_edit_path": reverse("studygroups_course_edit", args=(course.id,)),
        "created_at": course.created_at,
        "unlisted": course.unlisted,
        "discourse_topic_url": course.discourse_topic_url if course.discourse_topic_url else settings.PROTOCOL + '://' + settings.DOMAIN + reverse("studygroups_generate_course_discourse_topic", args=(course.id,)),
    }

    if hasattr(course, 'num_learning_circles'):
        data["learning_circles"] = course.num_learning_circles

    return data


class CourseListView(View):
    def get(self, request):
        query_schema = {
            "offset": schema.integer(),
            "limit": schema.integer(),
            "order": lambda v: (v, None) if v in ['title', 'usage', 'overall_rating', 'created_at', None] else (None, "must be 'title', 'usage', 'created_at', or 'overall_rating'"),
            "user": schema.boolean(),
            "include_unlisted": schema.boolean(),
            "facilitator_guide": schema.boolean(),
        }
        data = schema.django_get_to_dict(request.GET)
        clean_data, errors = schema.validate(query_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        courses = Course.objects.active().filter(archived=False)

        # include_unlisted must be != false and the query must be scoped
        # by user to avoid filtering out unlisted courses
        if request.GET.get('include_unlisted', "false") == "false" or 'user' not in request.GET:
            # return only courses that is not unlisted
            # if the user is part of a team, include unlisted courses from the team
            if request.user.is_authenticated:
                team_query = TeamMembership.objects.active().filter(user=request.user).values('team')
                team_ids = TeamMembership.objects.active().filter(team__in=team_query).values('user')
                courses = courses.filter(Q(unlisted=False) | Q(unlisted=True, created_by__in=team_ids))
            else:
                courses = courses.filter(unlisted=False)

        # TODO this doesn't exclude drafts
        courses = courses.annotate(
            num_learning_circles=Sum(
                Case(
                    When(
                        studygroup__deleted_at__isnull=True, then=Value(1),
                        studygroup__course__id=F('id')
                    ),
                    default=Value(0), output_field=models.IntegerField()
                )
            )
        )

        if 'user' in request.GET:
            user_id = request.user.id
            courses = courses.filter(created_by=user_id)

        if 'course_id' in request.GET:
            course_id = request.GET.get('course_id')
            courses = courses.filter(pk=int(course_id))

        order = request.GET.get('order', None)
        if order in ['title', None]:
            courses = courses.order_by('title')
        elif order == 'overall_rating':
            courses = courses.order_by('-overall_rating', '-total_ratings', 'title')
        elif order == 'created_at':
            courses = courses.order_by('-created_at')
        else:
            courses = courses.order_by('-num_learning_circles', 'title')

        query = request.GET.get('q', '').strip()

        if query:
            tsquery = CustomSearchQuery(query, config='simple')
            courses = courses.annotate(
                search=SearchVector('topics', 'title', 'caption', 'provider', config='simple')
            ).filter(search=tsquery)

        if 'topics' in request.GET:
            topics = request.GET.get('topics').split(',')
            query = Q(topics__icontains=topics[0])
            for topic in topics[1:]:
                query = Q(topics__icontains=topic) | query
            courses = courses.filter(query)

        if 'languages' in request.GET:
            languages = request.GET.get('languages').split(',')
            courses = courses.filter(language__in=languages)

        if 'oer' in request.GET and request.GET.get('oer', False) == 'true':
            courses = courses.filter(license__in=Course.OER_LICENSES)

        if clean_data.get('facilitator_guide'):
            courses = courses.filter(id__in=FacilitatorGuide.objects.active().values('course_id'))

        if 'active' in request.GET:
            active = request.GET.get('active') == 'true'
            study_group_ids = Meeting.objects.active().filter(
                meeting_date__gte=timezone.now()
            ).values('study_group')
            course_ids = None
            if active:
                course_ids = StudyGroup.objects.published().filter(id__in=study_group_ids).values('course')
            else:
                course_ids = StudyGroup.objects.published().exclude(id__in=study_group_ids).values('course')
            courses = courses.filter(id__in=course_ids)

        data = {
            'count': courses.count()
        }
        if 'offset' in request.GET or 'limit' in request.GET:
            limit, offset = _limit_offset(request)
            data['offset'] = offset
            data['limit'] = limit
            courses = courses[offset:offset+limit]

        data['items'] = [ serialize_course(course) for course in courses ]
        return json_response(request, data)


class CourseTopicListView(View):
    """ Return topics for listed courses """
    def get(self, request):
        topics = Course.objects.active()\
                .filter(unlisted=False)\
                .exclude(topics='')\
                .values_list('topics')
        topics = [
            item.strip().lower() for sublist in topics for item in sublist[0].split(',')
        ]
        from collections import Counter
        data = {}
        data['topics'] = { k: v for k, v in list(Counter(topics).items()) }
        return json_response(request, data)


def _image_check():
    def _validate(value):
        if value.startswith(settings.MEDIA_URL):
            return value.replace(settings.MEDIA_URL, '', 1), None
        else:
            return None, 'Image must be a valid URL for an existing file'
    return _validate


def _user_check(user):
    def _validate(value):
        if value is False:
            if user.profile.email_confirmed_at is None:
                return None, 'Users with unconfirmed email addresses cannot publish courses'
        return value, None
    return _validate


def _studygroup_check(studygroup_id):
    if not StudyGroup.objects.filter(pk=int(studygroup_id)).exists():
        return None, 'Learning circle matching ID not found'
    else:
        return StudyGroup.objects.get(pk=int(studygroup_id)), None


def _venue_name_check(venue_name):
    if len(slugify(venue_name, allow_unicode=True)):
        return venue_name, None
    return None, 'Venue name should include at least one alpha-numeric character.'


def _meetings_validator(meetings):
    if len(meetings) == 0:
        return None, 'Need to specify at least one meeting'
    meeting_schema = schema.schema({   
        "meeting_date": schema.date(),
        "meeting_time": schema.time()
    })
    results = list(map(meeting_schema, meetings))
    errors = list(filter(lambda x: x, map(lambda x: x[1], results)))
    mtngs = list(map(lambda x: x[0], results))
    if errors:
        return None, 'Invalid meeting data'
    else:
        return mtngs, None


def _facilitators_validator(facilitators):
    # TODO - check that its a list, facilitator exists and is part of same team
    if facilitators is None:
        return [], None
    if not isinstance(facilitators, list):
        return None, 'Invalid facilitators'
    members_in_team = get_team_users(facilitators[0])
    members_in_team_list = list(map(lambda x: x.id, members_in_team))
    if not all(item in members_in_team_list for item in facilitators):
        return None, 'Facilitators not part of the same team'
    results = list(map(schema.integer(), facilitators))
    errors = list(filter(lambda x: x, map(lambda x: x[1], results)))
    fcltrs = list(map(lambda x: x[0], results))
    if errors:
        return None, 'Invalid meeting data'
    else:
        return fcltrs, None


def _make_learning_circle_schema(request):

    post_schema = {
        "name": schema.text(length=128, required=False),
        "course": schema.chain([
            schema.integer(),
            _course_check,
        ], required=True),
        "description": schema.text(required=True, length=2000),
        "course_description": schema.text(required=False, length=2000),
        "venue_name": schema.chain([
            schema.text(required=True, length=256),
            _venue_name_check,
        ], required=True),
        "venue_details": schema.text(required=True, length=128),
        "venue_address": schema.text(required=True, length=256),
        "venue_website": schema.text(length=256),
        "city": schema.text(required=True, length=256),
        "region": schema.text(required=True, length=256),
        "country": schema.text(required=True, length=256),
        "country_en": schema.text(required=True, length=256),
        "latitude": schema.floating_point(),
        "longitude": schema.floating_point(),
        "place_id": schema.text(length=256),
        "language": schema.text(required=True, length=6),
        "online": schema.boolean(),
        "meeting_time": schema.time(required=True),
        "duration": schema.integer(required=True),
        "timezone": schema.text(required=True, length=128),
        "signup_question": schema.text(length=256),
        "facilitators": _facilitators_validator,
        "facilitator_goal": schema.text(length=256),
        "facilitator_concerns": schema.text(length=256),
        "image_url": schema.chain([
            schema.text(),
            _image_check(),
        ], required=False),
        "draft": schema.boolean(),
        "meetings": _meetings_validator,
    }
    return post_schema


@method_decorator(login_required, name='dispatch')
class LearningCircleCreateView(View):
    def post(self, request):
        post_schema = _make_learning_circle_schema(request)
        data = json.loads(request.body)
        data, errors = schema.validate(post_schema, data)
        if errors != {}:
            logger.debug('schema error {0}'.format(json.dumps(errors)))
            return json_response(request, {"status": "error", "errors": errors})

        # start and end dates need to be set for db model to be valid
        start_date = data.get('meetings')[0].get('meeting_date')
        end_date = data.get('meetings')[-1].get('meeting_date')

        # create learning circle
        study_group = StudyGroup(
            name=data.get('name', None),
            course=data.get('course'),
            course_description=data.get('course_description', None),
            facilitator=request.user,
            description=data.get('description'),
            venue_name=data.get('venue_name'),
            venue_address=data.get('venue_address'),
            venue_details=data.get('venue_details'),
            venue_website=data.get('venue_website', ''),
            city=data.get('city'),
            region=data.get('region'),
            country=data.get('country'),
            country_en=data.get('country_en'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            place_id=data.get('place_id', ''),
            online=data.get('online', False),
            language=data.get('language'),
            start_date=start_date,
            end_date=end_date,
            meeting_time=data.get('meeting_time'),
            duration=data.get('duration'),
            timezone=data.get('timezone'),
            image=data.get('image_url'),
            signup_question=data.get('signup_question', ''),
            facilitator_goal=data.get('facilitator_goal', ''),
            facilitator_concerns=data.get('facilitator_concerns', '')
        )

        # use course.caption if course_description is not set
        if study_group.course_description is None:
            study_group.course_description = study_group.course.caption

        # use course.title if name is not set
        if study_group.name is None:
            study_group.name = study_group.course.title

        # only update value for draft if the use verified their email address
        if request.user.profile.email_confirmed_at is not None:
            study_group.draft = data.get('draft', True)

        study_group.save()

        # notification about new study group is sent at this point, but no associated meetings exists, which implies that the reminder can't use the date of the first meeting
        generate_meetings_from_dates(study_group, data.get('meetings', []))

        # add all facilitators
        facilitators = set([request.user.id] + data.get('facilitators'))  # make user a facilitator
        for user_id in facilitators:
            f = Facilitator(study_group=study_group, user_id=user_id)
            f.save()
            if user_id != request.user.id:
                send_cofacilitator_email.delay(study_group.id, user_id, request.user.id)

        studygroup_url = f"{settings.PROTOCOL}://{settings.DOMAIN}" + reverse('studygroups_view_study_group', args=(study_group.id,))
        return json_response(request, { "status": "created", "studygroup_url": studygroup_url })


@method_decorator(user_is_group_facilitator, name='dispatch')
@method_decorator(login_required, name='dispatch')
class LearningCircleUpdateView(SingleObjectMixin, View):
    model = StudyGroup
    pk_url_kwarg = 'study_group_id'

    def post(self, request, *args, **kwargs):
        study_group = self.get_object()
        post_schema = _make_learning_circle_schema(request)
        data = json.loads(request.body)
        data, errors = schema.validate(post_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        if len(data.get('facilitators', [])) == 0:
            errors = { 'facilitators': ['Cannot remove all faclitators from a learning circle']}
            return json_response(request, {"status": "error", "errors": errors})


        # determine if meeting reminders should be regenerated
        regenerate_reminders = any([
            study_group.name != data.get('name'),
            study_group.venue_name != data.get('venue_name'),
            study_group.venue_address != data.get('venue_address'),
            study_group.venue_details != data.get('venue_details'),
            study_group.venue_details != data.get('venue_details'),
            study_group.language != data.get('language'),
        ])

        # update learning circle
        published = False
        draft = data.get('draft', True)
        # only publish a learning circle for a user with a verified email address
        if draft is False and request.user.profile.email_confirmed_at is not None:
            published = study_group.draft is True
            study_group.draft = False

        study_group.name = data.get('name', None)
        study_group.course = data.get('course')
        study_group.description = data.get('description')
        study_group.course_description = data.get('course_description', None)
        study_group.venue_name = data.get('venue_name')
        study_group.venue_address = data.get('venue_address')
        study_group.venue_details = data.get('venue_details')
        study_group.venue_website = data.get('venue_website', '')
        study_group.city = data.get('city')
        study_group.region = data.get('region')
        study_group.country = data.get('country')
        study_group.country_en = data.get('country_en')
        study_group.latitude = data.get('latitude')
        study_group.longitude = data.get('longitude')
        study_group.place_id = data.get('place_id', '')
        study_group.language = data.get('language')
        study_group.online = data.get('online')
        study_group.meeting_time = data.get('meeting_time')
        study_group.duration = data.get('duration')
        study_group.timezone = data.get('timezone')
        study_group.image = data.get('image_url')
        study_group.signup_question = data.get('signup_question', '')
        study_group.facilitator_goal = data.get('facilitator_goal', '')
        study_group.facilitator_concerns = data.get('facilitator_concerns', '')

        study_group.save()
        generate_meetings_from_dates(study_group, data.get('meetings', []))

        if regenerate_reminders:
            for meeting in study_group.meeting_set.active():
                # if the reminder hasn't already been sent, regenerate it
                if not Reminder.objects.filter(study_group_meeting=meeting, sent_at__isnull=False).exists():
                    generate_meeting_reminder(meeting)

        # update facilitators
        current_facilicators_ids = study_group.cofacilitators.all().values_list('user_id', flat=True)
        print(f'current facilitators {current_facilicators_ids}')
        updated_facilitators = data.get('facilitators')
        print(f'post value {updated_facilitators}')
        to_delete = study_group.cofacilitators.exclude(user_id__in=updated_facilitators)
        for facilitator in to_delete:
            send_cofacilitator_removed_email.delay(study_group.id, facilitator.user_id, request.user.id)
        print(f'to delete: {to_delete}')
        to_delete.delete()
        to_add = [f_id for f_id in updated_facilitators if f_id not in current_facilicators_ids]
        print(f'to add: {to_add}')
        for user_id in to_add:
            f = Facilitator(study_group=study_group, user_id=user_id)
            f.save()
            send_cofacilitator_email.delay(study_group.pk, user_id, request.user.id)
        
        studygroup_url = f"{settings.PROTOCOL}://{settings.DOMAIN}" + reverse('studygroups_view_study_group', args=(study_group.id,))
        return json_response(request, { "status": "updated", "studygroup_url": studygroup_url })


@method_decorator(csrf_exempt, name="dispatch")
class SignupView(View):
    def post(self, request):
        signup_questions = {
            "goals": schema.text(required=True),
            "support": schema.text(required=True),
            "custom_question": schema.text(),
        }
        post_schema = {
            "learning_circle": schema.chain([
                schema.integer(),
                lambda x: (None, 'No matching learning circle exists') if not StudyGroup.objects.filter(pk=int(x)).exists() else (StudyGroup.objects.get(pk=int(x)), None),
            ], required=True),
            "name": schema.text(required=True),
            "email": schema.email(required=True),
            "communications_opt_in": schema.boolean(),
            "consent": schema.chain([
                schema.boolean(),
                lambda consent: (None, 'Consent is needed to sign up') if not consent else (consent, None),
            ], required=True),
            "mobile": schema.mobile(),
            "signup_questions": schema.schema(signup_questions, required=True)
        }
        data = json.loads(request.body)
        clean_data, errors = schema.validate(post_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        study_group = clean_data.get('learning_circle')

        # Not sure how to cleanly implement validation like this using the schema?
        if study_group.signup_question:
            if not clean_data.get('signup_questions').get('custom_question'):
                return json_response(request, {"status": "error", "errors": { "signup_questions": [{"custom_question": ["Field is required"]}]}})

        if Application.objects.active().filter(email__iexact=clean_data.get('email'), study_group=study_group).exists():
            application = Application.objects.active().get(email__iexact=clean_data.get('email'), study_group=study_group)
        else:
            application = Application(
                study_group=study_group,
                name=clean_data.get('name'),
                email=clean_data.get('email'),
                accepted_at=timezone.now()
            )
        application.name = clean_data.get('name')
        application.signup_questions = json.dumps(clean_data.get('signup_questions'))
        if clean_data.get('mobile'):
            application.mobile = clean_data.get('mobile')
        application.communications_opt_in = clean_data.get('communications_opt_in', False)
        application.save()
        return json_response(request, {"status": "created"})


class ImageUploadView(View):
    def post(self, request):
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            storage = get_storage_class()()
            filename = storage.save(image.name, image)
            # TODO - get full URL
            image_url = ''.join([settings.MEDIA_URL, filename])
            return json_response(request, {"image_url": image_url})
        else:
            return json_response(request, {'error': 'not a valid image'})


def detect_platform_from_url(request):
    url = request.GET.get('url', "")
    platform = course_platform_from_url(url)

    return json_response(request, { "platform": platform })


class CourseLanguageListView(View):
    """ Return langugages for listed courses """
    def get(self, request):
        languages = Course.objects.active().filter(unlisted=False).values_list('language', flat=True)
        languages = set(languages)
        languages_dict = [
            get_language_info(language) for language in languages
        ]

        data = { "languages": languages_dict }
        return json_response(request, data)


class FinalReportListView(View):
    def get(self, request):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        studygroups = StudyGroup.objects.published().annotate(surveys=Count('learnersurveyresponse')).filter(surveys__gt=0, end_date__lt=today).order_by('-end_date')

        data = {}

        if 'offset' in request.GET or 'limit' in request.GET:
            limit, offset = _limit_offset(request)
            data['offset'] = offset
            data['limit'] = limit
            studygroups = studygroups[offset:offset+limit]

        def _map(sg):
            data = serialize_learning_circle(sg)
            if request.user.is_authenticated:
                data['signup_count'] = sg.application_set.active().count()
            return data

        data['items'] = [ _map(sg) for sg in studygroups ]

        return json_response(request, data)


class InstagramFeed(View):
    def get(self, request):
        """ Get user media from Instagram Basic Diplay API """
        """ https://developers.facebook.com/docs/instagram-basic-display-api/reference/media """
        url = "https://graph.instagram.com/me/media?fields=id,permalink&access_token={}".format(settings.INSTAGRAM_TOKEN)
        try:
            response = get_json_response(url)

            if response.get("data", None):
                return json_response(request, { "items": response["data"] })

            if response.get("error", None):
                return json_response(request, { "status": "error", "errors": response["error"]["message"] })
                logger.error('Could not make request to Instagram: {}'.format(response["error"]["message"]))

            return json_response(request, { "status": "error", "errors": "Could not make request to Instagram" })
        except ConnectionError as e:
            logger.error('Could not make request to Instagram')
            return json_response(request, { "status": "error", "errors": str(e) })



def serialize_team_data(team):
    serialized_team = {
        "id": team.pk,
        "name": team.name,
        "subtitle": team.subtitle,
        "page_slug": team.page_slug,
        "member_count": team.teammembership_set.active().count(),
        "zoom": team.zoom,
        "date_established": team.created_at.strftime("%B %Y"),
        "intro_text": team.intro_text,
        "website": team.website,
        "email_address": team.email_address,
        "location": team.location,
        "facilitators": [],
        "membership": team.membership,
    }

    members = team.teammembership_set.active().values('user')
    studygroup_count = StudyGroup.objects.published().filter(facilitator__in=members).count()

    serialized_team["studygroup_count"] = studygroup_count

    facilitators = team.teammembership_set.active()
    for facilitator in facilitators:
        facilitator_role = "FACILITATOR" if facilitator.role == TeamMembership.MEMBER else facilitator.role
        serialized_facilitator = {
            "first_name": facilitator.user.first_name,
            "city": facilitator.user.profile.city,
            "bio": facilitator.user.profile.bio,
            "contact_url": facilitator.user.profile.contact_url,
            "role": facilitator_role,
        }

        if facilitator.user.profile.avatar:
            serialized_facilitator["avatar_url"] = f"{settings.PROTOCOL}://{settings.DOMAIN}" + facilitator.user.profile.avatar.url

        serialized_team["facilitators"].append(serialized_facilitator)

    if team.page_image:
        serialized_team["image_url"] = f"{settings.PROTOCOL}://{settings.DOMAIN}" + team.page_image.url

    if team.logo:
        serialized_team["logo_url"] = f"{settings.PROTOCOL}://{settings.DOMAIN}" + team.logo.url

    if team.latitude and team.longitude:
        serialized_team["coordinates"] = {
            "longitude": team.longitude,
            "latitude": team.latitude,
        }

    return serialized_team


class TeamListView(View):
    def get(self, request):
        data = {}

        teams = Team.objects.all().order_by('name')

        data["count"] = teams.count()

        if 'image' in request.GET and request.GET.get('image') == "true":
            teams = teams.exclude(page_image="")


        if 'offset' in request.GET or 'limit' in request.GET:
            limit, offset = _limit_offset(request)
            data['offset'] = offset
            data['limit'] = limit
            teams = teams[offset:offset+limit]

        data['items'] = [ serialize_team_data(team) for team in teams ]

        return json_response(request, data)


class TeamDetailView(SingleObjectMixin, View):
    model = Team
    pk_url_kwarg = 'team_id'

    def get(self, request, **kwargs):
        data = {}
        team = self.get_object()
        serialized_team = serialize_team_data(team)

        if request.user.is_authenticated and team.teammembership_set.active().filter(user=request.user, role=TeamMembership.ORGANIZER).exists():
            #  ensure user is team organizer
            serialized_team['team_invitation_link'] = team.team_invitation_link()

        data['item'] = serialized_team

        return json_response(request, data)


def serialize_team_membership(tm):
    role_label = dict(TeamMembership.ROLES)[tm.role]
    email_validated = hasattr(tm.user, 'profile') and tm.user.profile.email_confirmed_at is not None
    email_confirmed_at = tm.user.profile.email_confirmed_at.strftime("%-d %B %Y") if email_validated else "--"

    return {
        "facilitator": {
            "first_name": tm.user.first_name,
            "last_name": tm.user.last_name,
            "email": tm.user.email,
            "email_confirmed_at": email_confirmed_at
        },
        "role": role_label,
        "id": tm.id,
    }

def serialize_team_invitation(ti):
    role_label = dict(TeamMembership.ROLES)[ti.role]
    return {
        "facilitator": {
            "email": ti.email,
        },
        "created_at": ti.created_at.strftime("%-d %B %Y"),
        "role": role_label,
        "id": ti.id,
    }


@method_decorator(login_required, name="dispatch")
class TeamMembershipListView(View):

    def get(self, request, **kwargs):
        query_schema = {
            "offset": schema.integer(),
            "limit": schema.integer(),
            "team_id": schema.integer(required=True),
        }

        data = schema.django_get_to_dict(request.GET)
        clean_data, errors = schema.validate(query_schema, data)
        team_id = clean_data["team_id"]

        user_is_team_organizer = TeamMembership.objects.active().filter(team=team_id, user=request.user, role=TeamMembership.ORGANIZER).exists()
        if not user_is_team_organizer:
            return HttpResponseForbidden()

        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        team_memberships = TeamMembership.objects.active().filter(team=team_id)

        data = {
            'count': team_memberships.count()
        }

        if 'offset' in request.GET or 'limit' in request.GET:
            limit, offset = _limit_offset(request)
            data['offset'] = offset
            data['limit'] = limit
            team_memberships = team_memberships[offset:offset+limit]

        data['items'] = [serialize_team_membership(m) for m in team_memberships]

        return json_response(request, data)



@method_decorator(login_required, name="dispatch")
class TeamInvitationListView(View):

    def get(self, request, **kwargs):
        query_schema = {
            "offset": schema.integer(),
            "limit": schema.integer(),
            "team_id": schema.integer(required=True)
        }

        data = schema.django_get_to_dict(request.GET)
        clean_data, errors = schema.validate(query_schema, data)
        team_id = clean_data["team_id"]

        user_is_team_organizer = TeamMembership.objects.active().filter(team=team_id, user=request.user, role=TeamMembership.ORGANIZER).exists()
        if not user_is_team_organizer:
            return HttpResponseForbidden()

        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        team_invitations = TeamInvitation.objects.filter(team=team_id, responded_at__isnull=True)

        data = {
            'count': team_invitations.count()
        }

        if 'offset' in request.GET or 'limit' in request.GET:
            limit, offset = _limit_offset(request)
            data['offset'] = offset
            data['limit'] = limit
            team_invitations = team_invitations[offset:offset+limit]

        data['items'] = [serialize_team_invitation(i) for i in team_invitations]

        return json_response(request, data)


def serialize_invitation_notification(invitation):
    return {
        "team_name": invitation.team.name,
        "team_organizer_name": invitation.organizer.first_name,
        "team_invitation_confirmation_url": reverse("studygroups_facilitator_invitation_confirm", args=(invitation.id,)),
    }

@login_required
def facilitator_invitation_notifications(request):
    email_validated = hasattr(request.user, 'profile') and request.user.profile.email_confirmed_at is not None
    pending_invitations = TeamInvitation.objects.filter(email__iexact=request.user.email, responded_at__isnull=True)
    eligible_team = eligible_team_by_email_domain(request.user)

    invitation_notifications = [ serialize_invitation_notification(i) for i in pending_invitations]

    if email_validated and eligible_team:
        implicit_invitation_notification = {
            'team_name': eligible_team.name,
            'team_invitation_confirmation_url': reverse("studygroups_facilitator_invitation_confirm")
        }
        invitation_notifications.append(implicit_invitation_notification)

    data = {
        "items": invitation_notifications
    }

    return json_response(request, data)


@user_is_team_organizer
@login_required
@require_http_methods(["POST"])
def create_team_invitation_link(request, team_id):
    team = Team.objects.get(pk=team_id)
    team.generate_invitation_token()

    return json_response(request, { "status": "updated", "team_invitation_link": team.team_invitation_link() })


@user_is_team_organizer
@login_required
@require_http_methods(["POST"])
def delete_team_invitation_link(request, team_id):
    team = Team.objects.get(pk=team_id)
    team.invitation_token = None
    team.save()

    return json_response(request, { "status": "deleted", "team_invitation_link": None })

def serialize_announcement(announcement):
    return {
        "text": announcement.text,
        "link": announcement.link,
        "link_text": announcement.link_text,
        "color": announcement.color,
    }

class AnnouncementListView(View):
    def get(self, request):
        announcements = Announcement.objects.filter(display=True)
        data = {
            "count": announcements.count(),
            "items": [ serialize_announcement(announcement) for announcement in announcements ]
        }

        return json_response(request, data)


def cities(request):
    cities = StudyGroup.objects.published().annotate(city_len=Length('city')).filter(city_len__gt=1).values_list('city', flat=True).distinct('city')

    data = {
        "count": cities.count(),
        "items": [{ "label": city, "value": city } for city in cities]
    }

    return json_response(request, data)

