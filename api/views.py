import datetime
import dateutil.parser

from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.conf import settings
from django import http
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import StudyGroupMeeting
from studygroups.models import Team

from uxhelpers.utils import json_response

from django.views import View

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
        study_groups = StudyGroup.objects.active()
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
 
        data = [ _map_to_json(sg) for sg in study_groups ]
        return json_response(request, data)
 

class SignupView(View):
    def post(self, request):
        pass

