from django.core.urlresolvers import reverse
from django.views import View
from django.views.generic.edit import FormView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.db.models import Q, F, Case, When, Value, Sum, Min, Max
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.core.files.storage import get_storage_class
from django.conf import settings
from django.views.generic.detail import SingleObjectMixin
from django.contrib.postgres.search import SearchQuery

import json
import datetime
import re
import logging

logger = logging.getLogger(__name__)


from studygroups.decorators import user_is_group_facilitator
from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import Meeting
from studygroups.models import Team
from studygroups.models import generate_all_meetings

from uxhelpers.utils import json_response

from .geo import getLatLonDelta
from . import schema
from .forms import ImageForm

class CustomSearchQuery(SearchQuery):
    """ use to_tsquery to support partial matches """
    """ NOTE: This is potentially unsafe!!"""
    def as_sql(self, compiler, connection):
        query = re.sub(r'[!\'()|&\:=,\.\ \-\<\>@]+', ' ', self.value).strip()
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
    data = {
        "course": {
            "id": sg.course.pk,
            "title": sg.course.title,
            "provider": sg.course.provider,
            "link": sg.course.link
        },
        "facilitator": sg.facilitator.first_name + " " + sg.facilitator.last_name,
        "venue": sg.venue_name,
        "venue_address": sg.venue_address + ", " + sg.city,
        "city": sg.city,
        "region": sg.region,
        "country": sg.country,
        "country_en": sg.country_en,
        "latitude": sg.latitude,
        "longitude": sg.longitude,
        "place_id": sg.place_id,
        "day": sg.day(),
        "start_date": sg.start_date,
        "meeting_time": sg.meeting_time,
        "time_zone": sg.timezone_display(),
        "end_time": sg.end_time(),
        "weeks": sg.meeting_set.active().count(),
        "url": 'https://' + settings.DOMAIN + reverse('studygroups_signup', args=(slugify(sg.venue_name, allow_unicode=True), sg.id,)),
    }
    if sg.image:
        data["image_url"] = 'https://' + settings.DOMAIN + sg.image.url
    # TODO else set default image URL
    if hasattr(sg, 'next_meeting_date'):
        data["next_meeting_date"] = sg.next_meeting_date
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
        }
        data = schema.django_get_to_dict(request.GET)
        clean_data, errors = schema.validate(query_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        study_groups = StudyGroup.objects.published().order_by('id')

        if 'id' in request.GET:
            id = request.GET.get('id')
            study_groups = StudyGroup.objects.filter(pk=int(id))

        if 'q' in request.GET:
            q = request.GET.get('q')
            study_groups = study_groups.annotate(
                search =
                    SearchVector('city')
                    + SearchVector('course__title')
                    + SearchVector('course__provider')
                    + SearchVector('course__topics')
                    + SearchVector('venue_name')
                    + SearchVector('venue_address')
                    + SearchVector('venue_details')
                    + SearchVector('facilitator__first_name')
                    + SearchVector('facilitator__last_name')
            ).filter(search=q)

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
            members = team.teammembership_set.values('user')
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
        from collections import Counter
        data = {}
        #data['items'] = list(set(topics))
        data['topics'] = { k:v for k,v in list(Counter(topics).items()) }
        return json_response(request, data)


def _course_check(course_id):
    if not Course.objects.filter(pk=int(course_id)).exists():
        return None, 'Course matching ID not found'
    else:
        return Course.objects.get(pk=int(course_id)), None


def _course_to_json(course):
    return {
        "id": course.id,
        "title": course.title,
        "provider": course.provider,
        "link": course.link,
        "caption": course.caption,
        "on_demand": course.on_demand,
        "learning_circles": course.num_learning_circles,
        "topics": [t.strip() for t in course.topics.split(',')] if course.topics else [],
        "language": course.language,
    }

class CourseListView(View):
    def get(self, request):
        query_schema = {
            "offset": schema.integer(),
            "limit": schema.integer(),
            "order": lambda v: (v, None) if v in ['title', 'usage', None] else (None, "must be 'title' or 'usage'")
        }
        data = schema.django_get_to_dict(request.GET)
        clean_data, errors = schema.validate(query_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        courses = Course.objects.active().filter(unlisted=False).annotate(
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

        if 'course_id' in request.GET:
            course_id = request.GET.get('course_id')
            courses = courses.filter(pk=int(course_id))

        if request.GET.get('order', None) in ['title', None]:
            courses = courses.order_by('title')
        else:
            courses = courses.order_by('-num_learning_circles')

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
        #data['items'] = list(set(topics))
        data['topics'] = { k:v for k,v in list(Counter(topics).items()) }
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
        if value == False:
            if user.profile.email_confirmed_at == None:
                return None, 'Users with unconfirmed email addresses cannot publish courses'
        return value, None
    return _validate


def _studygroup_check(studygroup_id):
    if not StudyGroup.objects.filter(pk=int(studygroup_id)).exists():
        return None, 'Learning circle matching ID not found'
    else:
        return StudyGroup.objects.get(pk=int(studygroup_id)), None

def _make_learning_circle_schema(request):
    post_schema = {
        "course": schema.chain([
            schema.integer(),
            _course_check,
        ], required=True),
        "description": schema.text(required=True, length=500),
        "venue_name": schema.text(required=True, length=256),
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
        "image": schema.chain([
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
            logger.error('schema error {0}'.format(json.dumps(errors)))
            return json_response(request, {"status": "error", "errors": errors})

        # create learning circle
        end_date = data.get('start_date') + datetime.timedelta(weeks=data.get('weeks') - 1)
        study_group = StudyGroup(
            course=data.get('course'),
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
            start_date=data.get('start_date'),
            end_date=end_date,
            meeting_time=data.get('meeting_time'),
            duration=data.get('duration'),
            timezone=data.get('timezone'),
            image=data.get('image'),
            signup_question=data.get('signup_question', ''),
            facilitator_goal=data.get('facilitator_goal', ''),
            facilitator_concerns=data.get('facilitator_concerns', '')
        )
        # only update value for draft if the use verified their email address
        if request.user.profile.email_confirmed_at != None:
            study_group.draft = data.get('draft', True)
        study_group.save()

        # generate all meetings if the learning circle has been published
        if study_group.draft == False:
            generate_all_meetings(study_group)

        study_group_url = settings.DOMAIN + reverse('studygroups_signup', args=(slugify(study_group.venue_name, allow_unicode=True), study_group.id,))
        return json_response(request, { "status": "created", "url": study_group_url });


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

        # update learning circle
        end_date = data.get('start_date') + datetime.timedelta(weeks=data.get('weeks') - 1)

        published = False
        # only publish a learning circle for a user with a verified email address
        draft = data.get('draft', True)
        if draft == False and request.user.profile.email_confirmed_at != None:
            published = study_group.draft == True
            study_group.draft = False

        study_group.course = data.get('course')
        study_group.description = data.get('description')
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
        study_group.start_date = data.get('start_date')
        study_group.end_date = end_date
        study_group.meeting_time = data.get('meeting_time')
        study_group.duration = data.get('duration')
        study_group.timezone = data.get('timezone')
        study_group.image = data.get('image')
        study_group.signup_question = data.get('signup_question', '')
        study_group.facilitator_goal = data.get('facilitator_goal', '')
        study_group.facilitator_concerns = data.get('facilitator_concerns', '')
        study_group.save()

        # generate all meetings if the learning circle has been published
        if published:
            generate_all_meetings(study_group)

        study_group_url = settings.DOMAIN + reverse('studygroups_signup', args=(slugify(study_group.venue_name, allow_unicode=True), study_group.id,))
        return json_response(request, { "status": "updated", "url": study_group_url });


class SignupView(View):
    def post(self, request):
        signup_questions = {
            "goals": schema.text(required=True),
            "support": schema.text(required=True),
            "computer_access": schema.text(required=True),
            "use_internet": schema.text(required=True)
        }
        post_schema = {
            "study_group": schema.chain([
                schema.integer(),
                lambda x: (None, 'No matching learning circle exists') if not StudyGroup.objects.filter(pk=int(x)).exists() else (StudyGroup.objects.get(pk=int(x)), None),
            ], required=True),
            "name": schema.text(required=True),
            "email": schema.email(required=True),
            "mobile": schema.mobile(),
            "signup_questions": schema.schema(signup_questions, required=True)
        }
        data = json.loads(request.body)
        clean_data, errors = schema.validate(post_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        study_group = StudyGroup.objects.get(pk=data.get('study_group'))

        if Application.objects.active().filter(email__iexact=data.get('email'), study_group=study_group).exists():
            application = Application.objects.active().get(email__iexact=data.get('email'), study_group=study_group)
        else:
            application = Application(
                study_group=study_group,
                name=data.get('name'),
                email=data.get('email'),
                signup_questions=json.dumps(data.get('signup_questions')),
                accepted_at=timezone.now()
            )
        application.name = data.get('name')
        application.signup_questions = json.dumps(data.get('signup_questions'))
        if data.get('mobile'):
            application.mobile = data.get('mobile')
        application.save()
        return json_response(request, {"status": "created"});


class LandingPageLearningCirclesView(View):
    """ return upcoming learning circles for landing page """
    def get(self, request):

        # get learning circles with image & upcoming meetings
        study_groups = StudyGroup.objects.published().filter(
            meeting__meeting_date__gte=timezone.now(),
        ).annotate(
            next_meeting_date=Min('meeting__meeting_date')
        ).order_by('next_meeting_date')[:3]

        # if there are less than 3 with upcoming meetings and an image
        if study_groups.count() < 3:
            #pad with learning circles with the most recent meetings
            past_study_groups = StudyGroup.objects.published().filter(
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
            #"city_list": [v['city'] for v in cities],
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
