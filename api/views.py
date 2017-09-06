from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.conf import settings
from django import http
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.db.models import Q, F, Count, Case, When, Value, Sum
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector

import datetime
import dateutil.parser
import json


from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import StudyGroupMeeting
from studygroups.models import Team

from uxhelpers.utils import json_response
from geo import getLatLonDelta

import schema


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
        "latitude": sg.latitude,
        "longitude": sg.longitude,
        "day": sg.day(),
        "start_date": sg.start_date,
        "meeting_time": sg.meeting_time,
        "time_zone": sg.timezone_display(),
        "end_time": sg.end_time(),
        "weeks": sg.studygroupmeeting_set.active().count(),
        "url": "https://learningcircles.p2pu.org" + reverse('studygroups_signup', args=(slugify(sg.venue_name), sg.id,)),
    }
    if sg.image:
        data["image_url"] = "https://learningcircles.p2pu.org" + sg.image.url

    #TODO else set default image URL
    return data

def _intCommaList(csv):
    values = csv.split(',') if csv else []
    for value in values:
        try:
            int(value)
        except ValueError:
            return 'Not a list of integers seperated by commas'
    return None

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
        errors = schema.validate(query_schema, data)
        if errors <> {}:
            return json_response(request, {"status": "error", "errors": errors})

        study_groups = StudyGroup.objects.active().order_by('id')

        if 'q' in request.GET:
            q = request.GET.get('q')
            study_groups = study_groups.annotate(
                search=
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
        if not city is None:
            study_groups = study_groups.filter(city=city)

        team_id = request.GET.get('team_id')
        if not team_id is None:
            team = Team.objects.get(pk=team_id)
            members = team.teammembership_set.values('user')
            team_users = User.objects.filter(pk__in=members)
            study_groups = study_groups.filter(facilitator__in=team_users)

        if 'signup' in request.GET:
            signup_open = request.GET.get('signup') == 'open'
            study_groups = study_groups.filter(signup_open=signup_open)

        if 'active' in request.GET:
            active = request.GET.get('active') == 'true'
            study_group_ids = StudyGroupMeeting.objects.active().filter(
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
            lat_min = max(-90, latitude-lat_delta)
            lat_max = min(90, latitude+lat_delta)
            lon_min = max(-180, longitude-lon_delta)
            lon_max = min(180, longitude+lon_delta)
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
                #__week_day differst from datetime.weekday()
                # Monday should be 0
                weekday = int(weekday) + 2 % 7
                query = query | Q(start_date__week_day=weekday) if query else Q(start_date__week_day=weekday)
            study_groups = study_groups.filter(query)

        data = {
            'count': len(study_groups)
        }
        if 'offset' in request.GET or 'limit' in request.GET:
            try:
                offset = int(request.GET.get('offset', 0))
            except ValueError as e:
                offset = 0
            try: 
                limit = int(request.GET.get('limit', 100))
            except ValueError as e:
                limit = 100

            data['offset'] = offset
            data['limit'] = limit
            study_groups = study_groups[offset:offset+limit]
 
        data['items'] = [ _map_to_json(sg) for sg in study_groups ]
        return json_response(request, data)


@method_decorator(csrf_exempt, name='dispatch')
class LearningCircleTopicListView(View):
    """ Return topics for listed courses """
    def get(self, request):
        study_group_ids = StudyGroupMeeting.objects.active().filter(
            meeting_date__gte=timezone.now()
        ).values('study_group')
        course_ids = None
        course_ids = StudyGroup.objects.active().filter(id__in=study_group_ids).values('course')

        topics = Course.objects.active()\
                .filter(unlisted=False)\
                .filter(id__in=course_ids)\
                .exclude(topics='')\
                .values_list('topics')
        topics = [
            item.strip() for sublist in topics for item in sublist[0].split(',')
        ]
        from collections import Counter
        data = {}
        #data['items'] = list(set(topics))
        data['topics'] = { k:v for k,v in Counter(topics).items() }
        return json_response(request, data)


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
            "order": lambda v: None if v in ['title', 'usage', None] else "must be 'title' or 'usage'",
        }
        data = schema.django_get_to_dict(request.GET)
        errors = schema.validate(query_schema, data)
        if errors <> {}:
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
        if request.GET.get('order', None) in ['title', None]:
            courses = courses.order_by('title')
        else:
            courses = courses.order_by('-num_learning_circles')

        query = request.GET.get('q', None)
        if query:
            courses = courses.annotate(
                search=
                    SearchVector('title') 
                    + SearchVector('caption') 
                    + SearchVector('provider') 
                    + SearchVector('topics')
            ).filter(search=query)


        if 'topics' in request.GET:
            topics = request.GET.get('topics').split(',')
            query = Q(topics__icontains=topics[0])
            for topic in topics[1:]:
                query = Q(topics__icontains=topic) | query
            courses = courses.filter(query)

        if 'active' in request.GET:
            active = request.GET.get('active') == 'true'
            study_group_ids = StudyGroupMeeting.objects.active().filter(
                meeting_date__gte=timezone.now()
            ).values('study_group')
            course_ids = None
            if active:
                course_ids = StudyGroup.objects.active().filter(id__in=study_group_ids).values('course')
            else:
                course_ids = StudyGroup.objects.active().exclude(id__in=study_group_ids).values('course')
            courses = courses.filter(id__in=course_ids)

        data = {
            'count': courses.count()
        }
        if 'offset' in request.GET or 'limit' in request.GET:
            try:
                offset = int(request.GET.get('offset', 0))
            except ValueError as e:
                offset = 0
            try: 
                limit = int(request.GET.get('limit', 100))
            except ValueError as e:
                limit = 100

            data['offset'] = offset
            data['limit'] = limit
            courses = courses[offset:offset+limit]

        data['items'] = [ _course_to_json(course) for course in courses ]
        return json_response(request, data)


@method_decorator(csrf_exempt, name='dispatch')
class CourseTopicListView(View):
    """ Return topics for listed courses """
    def get(self, request):
        topics = Course.objects.active()\
                .filter(unlisted=False)\
                .exclude(topics='')\
                .values_list('topics')
        topics = [
            item.strip() for sublist in topics for item in sublist[0].split(',')
        ]
        from collections import Counter
        data = {}
        #data['items'] = list(set(topics))
        data['topics'] = { k:v for k,v in Counter(topics).items() }
        return json_response(request, data)


@method_decorator(csrf_exempt, name='dispatch')
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
                lambda x: 'No matching learning circle exists' if not StudyGroup.objects.filter(pk=int(x)).exists() else None,
            ], required=True),
            "name": schema.text(required=True), 
            "email": schema.email(required=True),
            "mobile": schema.mobile(),
            "signup_questions": schema.schema(signup_questions, required=True)
        }
        data = json.loads(request.body)
        errors = schema.validate(post_schema, data)
        if errors <> {}:
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
