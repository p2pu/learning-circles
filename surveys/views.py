import datetime
import json
import unicodecsv as csv

from django import http
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic.base import View
from django.views.generic import ListView
from django.views.generic import TemplateView

from studygroups.decorators import user_is_staff
from studygroups.models import StudyGroup

from .models import FacilitatorSurveyResponse
from .models import LearnerSurveyResponse
from .models import get_all_results


@method_decorator(user_is_staff, name='dispatch')
class ExportLearnerSurveysView(ListView):

    def get_queryset(self, *args, **kwargs):
        query_set = LearnerSurveyResponse.objects.all()
        study_group_id = kwargs.get('study_group_id')
        if kwargs.get('study_group_id'):
            study_group = get_object_or_404(StudyGroup, pk=study_group_id)
            query_set = query_set.filter(study_group=study_group)
        return query_set

    def csv(self, **kwargs):
        data = get_all_results(self.object_list)
        response = http.HttpResponse(content_type="text/csv")
        ts = timezone.now().utcnow().isoformat()
        response['Content-Disposition'] = 'attachment; filename="learner-surveys-{}.csv"'.format(ts)
        writer = csv.writer(response)
        writer.writerow(data['heading'])
        for row in data['data']:
            writer.writerow(row)
        return response

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset(*args, **kwargs)
        return self.csv(**kwargs)



