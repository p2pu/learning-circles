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


from studygroups.models import Application
from studygroups.models import StudyGroup
from studygroups.models import Course
from studygroups.models import TeamMembership
from ..decorators import user_is_staff
from learnwithpeople import __version__ as VERSION
from learnwithpeople import GIT_REVISION
from ..tasks import send_community_digest

from studygroups.forms import DigestGenerateForm


@method_decorator(user_is_staff, name='dispatch')
class StaffDashView(TemplateView):
    template_name = 'studygroups/staff_dash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['version'] = VERSION
        context['git_revision'] = GIT_REVISION
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
class ExportSignupsView(ListView):

    def get_queryset(self):
        return Application.objects.all().prefetch_related('study_group', 'study_group__course')


    def csv(self, **kwargs):
        response = http.HttpResponse(content_type="text/csv")
        ts = timezone.now().utcnow().isoformat()
        response['Content-Disposition'] = 'attachment; filename="signups-{}.csv"'.format(ts)
        signup_questions = ['support', 'goals', 'computer_access']
        field_names = [
            'id', 'uuid', 'study group id', 'study group uuid', 'study group name', 'course',
            'location', 'name', 'email', 'mobile', 'signed up at'
        ] + signup_questions + ['use_internet', 'survey completed', 'communications opt-in']
        writer = csv.writer(response)
        writer.writerow(field_names)
        for signup in self.object_list:
            signup_data = json.loads(signup.signup_questions)
            digital_literacy = 'n/a'
            if signup_data.get('use_internet'):
                digital_literacy = dict(Application.DIGITAL_LITERACY_CHOICES)[signup_data.get('use_internet')]
            writer.writerow(
                [
                    signup.id,
                    signup.uuid,
                    signup.study_group_id,
                    signup.study_group.uuid,
                    signup.study_group.name,
                    signup.study_group.course.title,
                    signup.study_group.venue_name,
                    signup.name,
                    signup.email,
                    signup.mobile,
                    signup.created_at,
                ] +
                [ signup_data.get(key, 'n/a') for key in signup_questions ] +
                [
                    digital_literacy,
                    'yes' if signup.learnersurveyresponse_set.count() else 'no'
                ] +
                [ signup.communications_opt_in ]
            )
        return response


    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.csv(**kwargs)


@method_decorator(user_is_staff, name='dispatch')
class ExportFacilitatorsView(ListView):

    def get_queryset(self):
        learning_circles = StudyGroup.objects.select_related('course').published().filter(facilitator__user_id=OuterRef('pk')).order_by('-start_date')
        return User.objects.all().annotate(
            learning_circle_count=Sum(
                Case(
                    When(
                        facilitator__study_group__deleted_at__isnull=True,
                        facilitator__study_group__draft=False,
                        then=Value(1),
                        facilitator__user__id=F('id')
                    ),
                    default=Value(0), output_field=IntegerField()
                )
            )
        ).annotate(
            last_learning_circle_date=Subquery(learning_circles.values('start_date')[:1]),
            last_learning_circle_name=Subquery(learning_circles.values('name')[:1]),
            last_learning_circle_course=Subquery(learning_circles.values('course__title')[:1]),
            last_learning_circle_venue=Subquery(learning_circles.values('venue_name')[:1])
        )


    def csv(self, **kwargs):
        response = http.HttpResponse(content_type="text/csv")
        ts = timezone.now().utcnow().isoformat()
        response['Content-Disposition'] = 'attachment; filename="facilitators-{}.csv"'.format(ts)
        field_names = ['name',
            'email',
            'date joined',
            'last login',
            'communication opt-in',
            'learning circles run',
            'last learning circle date',
            'last learning cirlce name',
            'last learning circle course',
            'last learning circle venue',
        ]
        writer = csv.writer(response)
        writer.writerow(field_names)
        for user in self.object_list:
            data = [
                ' '.join([user.first_name, user.last_name]),
                user.email,
                user.date_joined,
                user.last_login,
                user.profile.communication_opt_in if user.profile else False,
                user.learning_circle_count,
                user.last_learning_circle_date,
                user.last_learning_circle_name,
                user.last_learning_circle_course,
                user.last_learning_circle_venue,
            ]
            writer.writerow(data)
        return response


    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.csv(**kwargs)


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
