import datetime
import json
import unicodecsv as csv

from django import http
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic.base import View
from django.views.generic import ListView


from studygroups.models import Application
from studygroups.decorators import user_is_organizer
from studygroups.decorators import user_is_team_organizer

def _user_is_staff(user):
    return user.is_staff

@method_decorator(user_passes_test(_user_is_staff), name='dispatch')
class ExportSignupsView(ListView):

    def get_queryset(self):
        return Application.objects.all().prefetch_related('study_group', 'study_group__course')


    def get_context_data(self, **kwargs):
        context = super(ExportSignupsView, self).get_context_data(**kwargs)
        return context


    def csv(self, **kwargs):
        context = self.get_context_data(**kwargs)
        response = http.HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="signups.csv"'
        signup_questions = ['support', 'goals', 'computer_access']
        field_names = ['study group id', 'course', 'location', 'name', 'email', 'mobile', 'date'] + signup_questions + ['use_internet']
        writer = csv.writer(response)
        writer.writerow(field_names)
        for signup in self.object_list:
            signup_data = json.loads(signup.signup_questions)
            digital_literacy = 'n/a'
            if signup_data.get('use_internet'):
                digital_literacy = dict(Application.DIGITAL_LITERACY_CHOICES)[signup_data.get('use_internet')]
            writer.writerow(
                [
                    signup.study_group_id,
                    signup.study_group.course.title,
                    signup.study_group.venue_name,
                    signup.name,
                    signup.email,
                    signup.mobile,
                    signup.created_at,
                ] + 
                [ signup_data.get(key, 'n/a') for key in signup_questions ] +
                [ digital_literacy ]
            )
        return response


    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.csv(**kwargs)
