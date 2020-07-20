from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchQuery
from django.contrib.postgres.search import SearchVector
from django.core.files.storage import get_storage_class
from django.db import models
from django.db.models import Q, F, Case, When, Value, Sum, Min, Max, OuterRef, Subquery, Count
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
from studygroups.models import Application
from studygroups.models import Meeting
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import Announcement
from studygroups.models import generate_all_meetings
from studygroups.models import get_json_response
from studygroups.models.course import course_platform_from_url
from studygroups.models.team import eligible_team_by_email_domain

from uxhelpers.utils import json_response

from api.geo import getLatLonDelta
from api import schema
from api.forms import ImageForm

logger = logging.getLogger(__name__)


def studygroups(request):
    #TODO only accept GET requests
    # TODO remove this API endpoint, where is it currently being used??
    study_groups = StudyGroup.objects.published()
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
    """ use to_tsquery to support partial matches """
    """ NOTE: This is potentially unsafe!!"""
    def as_sql(self, compiler, connection):
        query = re.sub(r'[!\'()|&\:=,\.\ \-\<\>@]+', ' ', self.value).strip().lower()
        tsquery = ":* & ".join(query.split(' '))
        tsquery += ":*"
        params = [tsquery]
        if self.config:
            config_sql, config_params = compiler.compile(self.config)
            template = 'to_tsquery({}::regconfig, %s)'.format(config_sql)
            params = config_params + [tsquery]
        else:
            template = 'to_tsquery(%s)'
        if self.invert:
            template = '!!({})'.format(template)
        return template, params


def _map_to_json(sg):
    last_meeting = sg.last_meeting()
    today = datetime.date.today()
    signup_open = (sg.signup_open and last_meeting.meeting_date > today) if last_meeting else False

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
        "facilitator": sg.facilitator.first_name,
        "venue": sg.venue_name,
        "venue_address": sg.venue_address + ", " + sg.city,
        "city": sg.city,
        "region": sg.region,
        "country": sg.country,
        "country_en": sg.country_en,
        "latitude": sg.latitude,
        "longitude": sg.longitude,
        "place_id": sg.place_id,
        "language": sg.language,
        "day": sg.day(),
        "start_date": sg.start_date,
        "start_datetime": sg.local_start_date(),
        "meeting_time": sg.meeting_time,
        "time_zone": sg.timezone_display(),
        "end_time": sg.end_time(),
        "weeks": sg.weeks if sg.draft else sg.meeting_set.active().count(),
        "url": f"{settings.PROTOCOL}://{settings.DOMAIN}" + reverse('studygroups_signup', args=(slugify(sg.venue_name, allow_unicode=True), sg.id,)),
        "report_url": sg.report_url(),
        "studygroup_path": reverse('studygroups_view_study_group', args=(sg.id,)),
        "draft": sg.draft,
        "signup_count": sg.application_set.count(),
        "signup_open": signup_open,
        "last_meeting_date": last_meeting.meeting_date if last_meeting else sg.end_date,
    }

    if sg.image:
        data["image_url"] = settings.PROTOCOL + '://' + settings.DOMAIN + sg.image.url
    # TODO else set default image URL
    if hasattr(sg, 'next_meeting_date'):
        data["next_meeting_date"] = sg.next_meeting_date
    if hasattr(sg, 'last_meeting_date'):
        data["last_meeting_date"] = sg.last_meeting_date
    if sg.signup_question:
        data["signup_question"] = sg.signup_question
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
            "order": lambda v: (v, None) if v in ['name', 'start_date', 'created_at', None] else (None, "must be 'name', 'created_at', or 'start_date'"),
        }
        data = schema.django_get_to_dict(request.GET)
        clean_data, errors = schema.validate(query_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        study_groups = StudyGroup.objects.published().order_by('-id')
        if 'draft' in request.GET:
            study_groups = StudyGroup.objects.active().order_by('-id')
        if 'id' in request.GET:
            id = request.GET.get('id')
            study_groups = StudyGroup.objects.filter(pk=int(id))
        if 'user' in request.GET:
            user_id = request.user.id
            study_groups = study_groups.filter(facilitator=user_id)

        if 'scope' in request.GET:
            scope = request.GET.get('scope')
            today = datetime.date.today()
            active_meetings = Meeting.objects.filter(study_group=OuterRef('pk'), deleted_at__isnull=True).order_by('meeting_date')
            upcoming_meetings = Meeting.objects.filter(study_group=OuterRef('pk'), deleted_at__isnull=True, meeting_date__gte=today).order_by('meeting_date')

            if scope == "active":
                study_groups = study_groups\
                .annotate(last_meeting_date=Subquery(active_meetings.reverse().values('meeting_date')[:1]), next_meeting_date=Subquery(upcoming_meetings.values('meeting_date')[:1]))\
                .filter(Q(last_meeting_date__gte=today) | Q(draft=True))
            elif scope == "upcoming":
                study_groups = study_groups\
                .annotate(first_meeting_date=Subquery(active_meetings.values('meeting_date')[:1]), next_meeting_date=Subquery(upcoming_meetings.values('meeting_date')[:1]))\
                .filter(Q(first_meeting_date__gt=today) | Q(draft=True))
            elif scope == "current":
                study_groups = study_groups\
                .annotate(first_meeting_date=Subquery(active_meetings.values('meeting_date')[:1]), last_meeting_date=Subquery(active_meetings.reverse().values('meeting_date')[:1]), next_meeting_date=Subquery(upcoming_meetings.values('meeting_date')[:1]))\
                .filter(first_meeting_date__lte=today, last_meeting_date__gte=today)
            elif scope == "completed":
                study_groups = study_groups\
                .annotate(last_meeting_date=Subquery(active_meetings.reverse().values('meeting_date')[:1]))\
                .filter(last_meeting_date__lt=today)

        q = request.GET.get('q', None)
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
                    'facilitator__first_name',
                    'facilitator__last_name',
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
            team = Team.objects.get(pk=team_id)
            members = team.teammembership_set.active().values('user')
            team_users = User.objects.filter(pk__in=members)
            study_groups = study_groups.filter(facilitator__in=team_users)

        if 'signup' in request.GET:
            signup_open = request.GET.get('signup') == 'open'
            study_groups = study_groups.filter(signup_open=signup_open)

        if 'active' in request.GET:
            active = request.GET.get('active') == 'true'
            study_group_ids = Meeting.objects.active().filter(
                meeting_date__gte=timezone.now()
            ).values('study_group')
            if active:
                study_groups = study_groups.filter(id__in=study_group_ids)
            else:
                study_groups = study_groups.exclude(id__in=study_group_ids)

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

        order = request.GET.get('order', None)
        if order == 'name':
            study_groups = study_groups.order_by('name')
        elif order == 'start_date':
            study_groups = study_groups.order_by('-start_date')
        elif order == 'created_at':
            study_groups = study_groups.order_by('-created_at')

        data = {
            'count': len(study_groups)
        }

        if 'offset' in request.GET or 'limit' in request.GET:
            limit, offset = _limit_offset(request)
            data['offset'] = offset
            data['limit'] = limit
            study_groups = study_groups[offset:offset+limit]

        data['items'] = [ _map_to_json(sg) for sg in study_groups ]
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


def _course_to_json(course):
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

        query = request.GET.get('q', None)
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

        data['items'] = [ _course_to_json(course) for course in courses ]
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

def _make_learning_circle_schema(request):
    post_schema = {
        "name": schema.text(length=128, required=False),
        "course": schema.chain([
            schema.integer(),
            _course_check,
        ], required=True),
        "description": schema.text(required=True, length=500),
        "course_description": schema.text(required=False, length=500),
        "venue_name": schema.chain([
            schema.text(required=True, length=256),
            _venue_name_check,
        ], required=True),
        "venue_details": schema.text(required=True, length=128),
        "venue_address": schema.text(required=True, length=256),
        "venue_website": schema.text(),
        "city": schema.text(required=True, length=256),
        "region": schema.text(required=True, length=256),
        "country": schema.text(required=True, length=256),
        "country_en": schema.text(required=True, length=256),
        "latitude": schema.floating_point(),
        "longitude": schema.floating_point(),
        "place_id": schema.text(length=256),
        "language": schema.text(required=True, length=6),
        "start_date": schema.date(required=True),
        "weeks": schema.chain([
            schema.integer(required=True),
            lambda v: (None, 'Need to be at least 1') if v < 1 else (v, None),
        ]),
        "meeting_time": schema.time(required=True),
        "duration": schema.integer(required=True),
        "timezone": schema.text(required=True, length=128),
        "signup_question": schema.text(length=256),
        "facilitator_goal": schema.text(length=256),
        "facilitator_concerns": schema.text(length=256),
        "image_url": schema.chain([
            schema.text(),
            _image_check(),
        ], required=False),
        "draft": schema.boolean()
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

        # create learning circle
        end_date = data.get('start_date') + datetime.timedelta(weeks=data.get('weeks') - 1)
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
            language=data.get('language'),
            start_date=data.get('start_date'),
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

        # generate all meetings if the learning circle has been published
        if study_group.draft is False:
            generate_all_meetings(study_group)

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

        end_date = data.get('start_date') + datetime.timedelta(weeks=data.get('weeks') - 1)

        # if the date is changed, check if that is okay?
        date_changed = any([
            study_group.start_date != data.get('start_date'),
            study_group.end_date != end_date,
            study_group.meeting_time != data.get('meeting_time'),
        ])

        # check based on current value for start date
        if date_changed and not study_group.can_update_meeting_datetime():
            return json_response(request, {"status": "error", "errors": {"start_date": "cannot update date"}})

        # check based on new value for start date
        start_datetime = datetime.datetime.combine(
            data.get('start_date'),
            data.get('meeting_time')
        )
        tz = pytz.timezone(data.get('timezone'))
        start_datetime = tz.localize(start_datetime)
        if date_changed and start_datetime < timezone.now() + datetime.timedelta(days=2):
            return json_response(request, {"status": "error", "errors": {"start_date": "The start date must be at least 2 days from today"}})

        # update learning circle
        published = False
        # only publish a learning circle for a user with a verified email address
        draft = data.get('draft', True)
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
        study_group.start_date = data.get('start_date')
        study_group.end_date = end_date
        study_group.meeting_time = data.get('meeting_time')
        study_group.duration = data.get('duration')
        study_group.timezone = data.get('timezone')
        study_group.image = data.get('image_url')
        study_group.signup_question = data.get('signup_question', '')
        study_group.facilitator_goal = data.get('facilitator_goal', '')
        study_group.facilitator_concerns = data.get('facilitator_concerns', '')
        study_group.save()

        # generate all meetings if the learning circle has been published
        if published:
            generate_all_meetings(study_group)
        elif study_group.draft is False and date_changed:
            # if the lc was already published and the date was changed, update meetings
            study_group.meeting_set.delete()
            generate_all_meetings(study_group)

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


class LandingPageLearningCirclesView(View):
    """ return upcoming learning circles for landing page """
    def get(self, request):

        query_schema = {
            "scope": schema.text(),
        }
        data = schema.django_get_to_dict(request.GET)
        clean_data, errors = schema.validate(query_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        study_groups_unsliced = StudyGroup.objects.published()

        if 'scope' in request.GET and request.GET.get('scope') == "team":
            user = request.user
            team_ids = TeamMembership.objects.active().filter(user=user).values("team")

            if team_ids.count() == 0:
                return json_response(request, { "status": "error", "errors": ["User is not on a team."] })

            team_members = TeamMembership.objects.active().filter(team__in=team_ids).values("user")
            study_groups_unsliced = study_groups_unsliced.filter(facilitator__in=team_members)

        # get learning circles with image & upcoming meetings
        study_groups = study_groups_unsliced.filter(
            meeting__meeting_date__gte=timezone.now(),
        ).annotate(
            next_meeting_date=Min('meeting__meeting_date')
        ).order_by('next_meeting_date')[:3]

        # if there are less than 3 with upcoming meetings and an image
        if study_groups.count() < 3:
            # pad with learning circles with the most recent meetings
            past_study_groups = study_groups_unsliced.filter(
                meeting__meeting_date__lt=timezone.now(),
            ).annotate(
                next_meeting_date=Max('meeting__meeting_date')
            ).order_by('-next_meeting_date')
            study_groups = list(study_groups) + list(past_study_groups[:3-study_groups.count()])
        data = {
            'items': [ _map_to_json(sg) for sg in study_groups ]
        }
        return json_response(request, data)


class LandingPageStatsView(View):
    """ Return stats for the landing page """
    """
    - Number of active learning circles
    - Number of cities where learning circle happened
    - Number of facilitators who ran at least 1 learning circle
    - Number of learning circles to date
    """
    def get(self, request):
        study_groups = StudyGroup.objects.published().filter(
            meeting__meeting_date__gte=timezone.now()
        ).annotate(
            next_meeting_date=Min('meeting__meeting_date')
        )
        cities = StudyGroup.objects.published().filter(
            latitude__isnull=False,
            longitude__isnull=False,
        ).distinct('city').values('city')
        learning_circle_count = StudyGroup.objects.published().count()
        facilitators = StudyGroup.objects.active().distinct('facilitator').values('facilitator')
        cities_s = list(set([c['city'].split(',')[0].strip() for c in cities]))
        data = {
            "active_learning_circles": study_groups.count(),
            "cities": len(cities_s),
            "facilitators": facilitators.count(),
            "learning_circle_count": learning_circle_count
        }
        return json_response(request, data)


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
            data = _map_to_json(sg)
            if request.user.is_authenticated:
                data['signup_count'] = sg.application_set.count()
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
        "page_slug": team.page_slug,
        "member_count": team.teammembership_set.active().count(),
        "zoom": team.zoom,
        "date_established": team.created_at.strftime("%B %Y"),
        "intro_text": team.intro_text,
        "website": team.website,
        "email_address": team.email_address,
        "location": team.location,
        "facilitators": [],
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
            serialized_team['team_invitation_url'] = team.team_invitation_url()

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
def create_team_invitation_url(request, team_id):
    team = Team.objects.get(pk=team_id)
    team.generate_invitation_token()

    return json_response(request, { "status": "updated", "team_invitation_url": team.team_invitation_url() })


@user_is_team_organizer
@login_required
@require_http_methods(["POST"])
def delete_team_invitation_url(request, team_id):
    team = Team.objects.get(pk=team_id)
    team.invitation_token = None
    team.save()

    return json_response(request, { "status": "deleted", "team_invitation_url": None })

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

