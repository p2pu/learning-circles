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
from django.contrib.auth.models import User

import datetime
import dateutil.parser
import json


from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import StudyGroupMeeting
from studygroups.models import Team

from uxhelpers.utils import json_response

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


class LearningCircleListView(View):
    def get(self, request):
        study_groups = StudyGroup.objects.active().order_by('id')

        if 'course_id' in request.GET:
            study_groups = study_groups.filter(course_id=request.GET.get('course_id'))
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
            study_group_ids = StudyGroupMeeting.objects.active().filter(meeting_date__gte=timezone.now()).values('study_group')
            if active:
                study_groups = study_groups.filter(id__in=study_group_ids)
            else:
                study_groups = study_groups.exclude(id__in=study_group_ids)

        data = {
            'count': study_groups.count()
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


def _course_to_json(course):
    return {
        "id": course.id,
        "title": course.title,
        "provider": course.provider,
        "link": course.link,
        "key": course.key,
        "start_date": course.start_date,
        "duration": course.duration,
        "prerequisite": course.prerequisite,
        "time_required": course.time_required,
        "caption": course.caption,
        "learning_circles": course.studygroup_set.active().count(),
    }

class CourseListView(View):
    def get(self, request):
        courses = Course.objects.order_by('title')
        # TODO filter by active learning circles
        query = request.GET.get('q', None)
        if query:
            courses = courses.filter(title__icontains=query)
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
