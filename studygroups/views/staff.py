from datetime import datetime, time
import json
import unicodecsv as csv

from django import http
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.db.models.expressions import RawSQL
from django.db.models import Count
from django.db.models import Q
from django.db.models import Prefetch
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models import F, Case, When, Value, Sum, IntegerField

from django_celery_results.models import TaskResult
from celery.result import AsyncResult

from studygroups.models import Application
from studygroups.models import StudyGroup
from studygroups.models import Course
from studygroups.models import TeamMembership
from ..decorators import user_is_staff
from learnwithpeople import __version__ as VERSION
from learnwithpeople import GIT_REVISION
from ..tasks import send_community_digest
from ..tasks import export_signups
from ..tasks import export_users
from ..tasks import export_learning_circles
from ..tasks import export_courses
from studygroups.forms import DigestGenerateForm

from uxhelpers.utils import json_response


@method_decorator(user_is_staff, name='dispatch')
class StaffDashView(TemplateView):
    template_name = 'studygroups/staff_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['version'] = VERSION
        context['git_revision'] = GIT_REVISION
        # TODO - see if there are any pending exports - Or recent exports

        return context


@method_decorator(user_is_staff, name='dispatch')
class DigestGenerateView(FormView):
    form_class = DigestGenerateForm
    template_name = 'studygroups/digest_form.html'
    success_url = reverse_lazy('studygroups_staff_dash')

    def form_valid(self, form):
        # Find all signups with email and send opt out confirmation
        messages.info(self.request, _('You will shortly receive the community digest.'))
        start_date = datetime.combine(form.cleaned_data['start_date'], time(0,0,0))
        start_date = timezone.utc.localize(start_date)
        end_date = datetime.combine(form.cleaned_data['end_date'], time(0,0,0))
        end_date = timezone.utc.localize(end_date)
        send_community_digest.delay(start_date, end_date)
        return super().form_valid(form)


@method_decorator(user_is_staff, name='dispatch')
class ExportStatusView(View):

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get('task_id')
        # TODO - check that the task was an export
        result = AsyncResult(task_id)
        task_data = {
            'task_id': result.task_id,
            'status': result.state,
            'result': result.result if result.state == 'SUCCESS' else None,
        }
        return json_response(request, task_data)


@method_decorator(user_is_staff, name='dispatch')
class ExportSignupsView(View):

    def get(self, request, *args, **kwargs):
        task = export_signups.delay(request.user.id)
        return json_response(request, {'task_id': task.id})


@method_decorator(user_is_staff, name='dispatch')
class ExportFacilitatorsView(View):

    def get(self, request, *args, **kwargs):
        task = export_users.delay()
        return json_response(request, {'task_id': task.id})


@method_decorator(user_is_staff, name='dispatch')
class ExportStudyGroupsView(View):

    def get(self, request, *args, **kwargs):
        task = export_learning_circles.delay()
        return json_response(request, {'task_id': task.id})


@method_decorator(user_is_staff, name='dispatch')
class ExportCoursesView(View):

    def get(self, request, *args, **kwargs):
        task = export_courses.delay()
        return json_response(request, {'task_id': task.id})
