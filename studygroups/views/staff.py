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
class ExportStudyGroupsView(ListView):

    def get_queryset(self):
        return StudyGroup.objects.all().prefetch_related('course', 'facilitator_set', 'meeting_set').annotate(
            learning_circle_number=RawSQL("RANK() OVER(PARTITION BY created_by_id ORDER BY created_at ASC)", [])
        )

    def csv(self, **kwargs):
        response = http.HttpResponse(content_type="text/csv")
        ts = timezone.now().utcnow().isoformat()
        response['Content-Disposition'] = 'attachment; filename="learning-circles-{}.csv"'.format(ts)
        field_names = [
            'id',
            'uuid',
            'name',
            'date created',
            'date deleted',
            'draft',
            'course id',
            'course title',
            'created by',
            'created by email',
            'learning_circle_number',
            'location',
            'city',
            'time',
            'day',
            'last meeting',
            'first meeting',
            'signups',
            'team',
            'facilitator survey',
            'facilitator survey completed',
            'learner survey',
            'learner survey responses',
            'did not happen',
            'facilitator count',
        ]
        writer = csv.writer(response)
        writer.writerow(field_names)
        for sg in self.object_list:
            data = [
                sg.pk,
                sg.uuid,
                sg.name,
                sg.created_at,
                sg.deleted_at,
                'yes' if sg.draft else 'no',
                sg.course.id,
                sg.course.title,
                ' '.join([sg.created_by.first_name, sg.created_by.last_name]),
                sg.created_by.email,
                sg.learning_circle_number,
                ' ' .join([sg.venue_name, sg.venue_address]),
                sg.city,
                sg.meeting_time,
                sg.day(),
            ]
            if sg.meeting_set.active().last():
                data += [sg.meeting_set.active().order_by('meeting_date', 'meeting_time').last().meeting_date]
            elif sg.deleted_at:
                data += [sg.start_date]
            else:
                data += ['']

            if sg.meeting_set.active().first():
                data += [sg.meeting_set.active().order_by('meeting_date', 'meeting_time').first().meeting_date]
            elif sg.deleted_at:
                data += [sg.end_date]
            else:
                data += ['']

            data += [sg.application_set.active().count()]

            if sg.team:
                data += [sg.team.name]
            else:
                data += ['']

            base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
            facilitator_survey =  '{}{}'.format(
                base_url,
                reverse('studygroups_facilitator_survey', args=(sg.uuid,))
            )
            data += [facilitator_survey]
            data += ['yes' if sg.facilitatorsurveyresponse_set.count() else 'no']
            learner_survey = '{}{}'.format(
                base_url,
                reverse('studygroups_learner_survey', args=(sg.uuid,))
            )
            data += [learner_survey]
            data += [sg.learnersurveyresponse_set.count()]
            data += [sg.did_not_happen]
            data += [sg.facilitator_set.count()]

            writer.writerow(data)
        return response


    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.csv(**kwargs)


@method_decorator(user_is_staff, name='dispatch')
class ExportCoursesView(ListView):

    def get_queryset(self):
        team_membership = TeamMembership.objects.active().filter(user=OuterRef('created_by'))
        return Course.objects.active()\
            .filter(studygroup__deleted_at__isnull=True, studygroup__draft=False)\
            .filter(facilitatorguide__deleted_at__isnull=True)\
            .annotate(lc_count=Count('studygroup', distinct=True))\
            .annotate(active_lc_count=Count('studygroup', distinct=True, filter=Q(studygroup__end_date__gte=timezone.now())))\
            .annotate(facilitator_guide_count=Count('facilitatorguide', distinct=True))\
            .annotate(team_name=Subquery(team_membership.values('team__name')[:1]))\
            .select_related('created_by')

    def csv(self, **kwargs):
        response = http.HttpResponse(content_type="text/csv")
        ts = timezone.now().utcnow().isoformat()
        response['Content-Disposition'] = 'attachment; filename="courses-{}.csv"'.format(ts)
        db_fields = [
            'id',
            'title',
            'provider',
            'link',
            'caption',
            'on_demand',
            'keywords',
            'language',
            'created_by',
            'unlisted',
            'license',
            'created_at',
            'lc_count',
            'active_lc_count',
            'facilitator_guide_count',
            'team_name',
        ]
        writer = csv.writer(response)
        writer.writerow(db_fields)
        for obj in self.object_list:
            data = [
                getattr(obj, field) for field in db_fields
            ]
            writer.writerow(data)
        return response

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.csv(**kwargs)
