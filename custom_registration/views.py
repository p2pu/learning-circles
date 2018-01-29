from django.core.urlresolvers import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.template.defaultfilters import slugify
from django.db.models import Q, F, Case, When, Value, Sum, Min, Max
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.postgres.search import SearchVector

import json
import datetime


from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import StudyGroupMeeting
from studygroups.models import Team
from studygroups.models import generate_all_meetings

from uxhelpers.utils import json_response

from api import schema
from .models import create_user

@method_decorator(csrf_exempt, name='dispatch')
class SignupApiView(View):
    def post(self, request):
        post_schema = {
            "email": schema.email(required=True),
            "first_name": schema.text(required=True),
            "last_name": schema.text(required=True),
            "password": schema.text(required=True),
            #"mailing_list_signups": schema.boolean(),
        }
        data = json.loads(request.body)
        data, errors = schema.validate(post_schema, data)
        if errors != {}:
            return json_response(request, {"status": "error", "errors": errors})

        # TODO add mailing list signup
        # TODO add password
        ## create user
        user = create_user(data['email'], data['first_name'], data['last_name'], False)
        # Sign user in
        login(request, user)

        return json_response(request, {"status": "created"});

