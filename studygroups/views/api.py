import datetime
import dateutil.parser

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from django import http
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import Feedback
from studygroups.models import StudyGroupMeeting
from studygroups.models import Team

from uxhelpers.utils import json_response


def studygroups(request):
    #TODO only accept GET requests
    # TODO remove this API endpoint, where is it currently being used??
    study_groups = StudyGroup.objects.published()
    if 'course_id' in request.GET:
        study_groups = study_groups.filter(course_id=request.GET.get('course_id'))
    
    def to_json(sg):
        data = {
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
            "weeks": sg.studygroupmeeting_set.active().count(),
            "url": "https://learningcircles.p2pu.org" + reverse('studygroups_signup', args=(slugify(sg.venue_name), sg.id,)),
        }
        if sg.image:
            data["image_url"] = "https://learningcircles.p2pu.org" + sg.image.url
        #TODO else set default image URL
        return data

    data = [ to_json(sg) for sg in study_groups ]
    return json_response(request, data)


