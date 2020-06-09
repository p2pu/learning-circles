import datetime
import json

from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django import http
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic.base import View
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic import ListView
from django.contrib import messages

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import Meeting
from studygroups.models import report_data
from studygroups.models import generate_all_meetings
from studygroups.models import Team
from studygroups.models import get_team_users
from studygroups.models import get_user_team
from studygroups.tasks import send_team_invitation_email
from studygroups.decorators import user_is_organizer
from studygroups.decorators import user_is_team_member
from studygroups.decorators import user_is_team_organizer
from studygroups.forms import OrganizerGuideForm
from studygroups.forms import TeamForm

@user_is_organizer
def organize(request):
    if not request.user.is_staff:
        # redirect user to team organizer page
        team = get_user_team(request.user)
        url = reverse('studygroups_organize_team', args=(team.id,))
        return http.HttpResponseRedirect(url)
    today = datetime.datetime.now().date()
    two_weeks_ago = today - datetime.timedelta(weeks=2, days=today.weekday())
    two_weeks = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(weeks=3)
    study_groups = StudyGroup.objects.published()
    facilitators = User.objects.all()
    courses = []  # TODO Remove courses until we implement course selection for teams
    invitations = []
    team=None

    active_study_groups = study_groups.filter(
        id__in=Meeting.objects.active().filter(meeting_date__gte=two_weeks_ago).values('study_group')
    )
    meetings = Meeting.objects.active()\
        .filter(study_group__in=study_groups, meeting_date__gte=two_weeks_ago)\
        .exclude(meeting_date__gte=two_weeks)

    context = {
        'team': team,
        'courses': courses,
        'meetings': meetings,
        'study_groups': study_groups,
        'active_study_groups': active_study_groups,
        'facilitators': facilitators,
        'invitations': invitations,
        'today': timezone.now(),
    }

    return render(request, 'studygroups/organize.html', context)


@user_is_team_organizer
def organize_team(request, team_id):
    today = datetime.datetime.now().date()
    two_weeks_ago = today - datetime.timedelta(weeks=2, days=today.weekday())
    two_weeks = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(weeks=3)
    team = get_object_or_404(Team, pk=team_id)

    members = team.teammembership_set.active().values('user')
    team_users = User.objects.filter(pk__in=members)
    study_groups = StudyGroup.objects.published().filter(facilitator__in=team_users)
    facilitators = team_users
    invitations = TeamInvitation.objects.filter(team=team, responded_at__isnull=True)
    active_study_groups = study_groups.filter(
        id__in=Meeting.objects.active().filter(meeting_date__gte=two_weeks_ago).values('study_group')
    )
    meetings = Meeting.objects.active()\
        .filter(study_group__in=study_groups, meeting_date__gte=two_weeks_ago)\
        .exclude(meeting_date__gte=two_weeks)

    context = {
        'team': team,
        'meetings': meetings,
        'study_groups': study_groups,
        'active_study_groups': active_study_groups,
        'facilitators': facilitators,
        'invitations': invitations,
        'today': timezone.now()
    }
    return render(request, 'studygroups/organize.html', context)


@method_decorator(user_is_organizer, name='dispatch')
class StudyGroupList(ListView):
    model = StudyGroup

    def get_queryset(self):
        study_groups = StudyGroup.objects.published()
        if not self.request.user.is_staff:
            team_users = get_team_users(self.request.user)
            study_groups = study_groups.filter(facilitator__in=team_users)
        return study_groups


@method_decorator(user_is_organizer, name='dispatch')
class MeetingList(ListView):
    model = Meeting

    def get_queryset(self):
        study_groups = StudyGroup.objects.published()
        if not self.request.user.is_staff:
            team_users = get_team_users(self.request.user)
            study_groups = study_groups.filter(facilitator__in=team_users)

        meetings = Meeting.objects.active().filter(study_group__in=study_groups)
        return meetings


@method_decorator(user_is_organizer, name='dispatch')
class TeamMembershipDelete(DeleteView):
    model = TeamMembership
    success_url = reverse_lazy('studygroups_organize')
    template_name = 'studygroups/confirm_delete_membership.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = TeamMembership.objects.active()
        return queryset.get(user_id=self.kwargs.get('user_id'), team_id=self.kwargs.get('team_id'))


@method_decorator(user_is_organizer, name='dispatch')
class CourseDelete(DeleteView):
    model = Course
    success_url = reverse_lazy('studygroups_organize')
    template_name = 'studygroups/confirm_delete.html'


@method_decorator(csrf_exempt, name='dispatch') #TODO need to send CSRF token in header
@method_decorator(user_is_team_organizer, name='dispatch')
class TeamInvitationCreate(View):

    def post(self, request, *args, **kwargs):
        team = Team.objects.get(pk=self.kwargs.get('team_id'))
        email = json.loads(request.body).get('email')
        email = BaseUserManager.normalize_email(email)
        # check email address
        try:
            validate_email(email)
        except ValidationError:
            return http.JsonResponse({
                "status": "ERROR",
                "errors": {"email": [_("invalid email address")]}
            })
        # make sure email not already invited to this team
        if TeamInvitation.objects.filter(team=team, email__iexact=email, responded_at__isnull=True).exists():
            return http.JsonResponse({
                "status": "ERROR",
                "errors": {
                    "_": [_("There is already a pending invitation for a user with this email address to join your team")]
                }
            })
        # make sure user not already part of this team
        if TeamMembership.objects.active().filter(team=team, user__email__iexact=email).exists():
            return http.JsonResponse({
                "status": "ERROR",
                "errors": {
                    "_": [_("User with the given email address is already part of your team.")]
                }
            })
        invitation = TeamInvitation.objects.create(
            team=team,
            organizer=request.user,
            email=email,
            role=TeamMembership.MEMBER
        )
        send_team_invitation_email(team, invitation.email, request.user)
        return http.JsonResponse({"status": "CREATED"})


@user_is_team_member
def weekly_report(request, year=None, month=None, day=None):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if month and day and year:
        today = today.replace(year=int(year), month=int(month), day=int(day))
    start_time = today - datetime.timedelta(days=today.weekday())
    end_time = start_time + datetime.timedelta(days=7)
    context = {
        'start_time': start_time,
        'end_time': end_time,
    }
    # get team for current user
    team = None
    membership = TeamMembership.objects.active().filter(user=request.user).first()
    if membership:
        team = membership.team

    data = report_data(start_time, end_time, team)
    context.update(data)

    return render(request, 'studygroups/email/weekly-update.html', context)


class OrganizerGuideForm(FormView):
    form_class = OrganizerGuideForm
    template_name = 'studygroups/get_organizer_guide.html'
    success_url = reverse_lazy('studygroups_facilitator')

    def get(self, request, *args, **kwargs):
        user = self.request.user
        # redirect to the guide on discourse if user is organizer
        if user.is_authenticated:
            if TeamMembership.objects.active().filter(user=user, role=TeamMembership.ORGANIZER).exists():
                url = 'https://community.p2pu.org/t/julianas-organizer-guide-how-to-start-a-learning-circle-community/3160'
                return http.HttpResponseRedirect(url)

        return super(OrganizerGuideForm, self).get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(OrganizerGuideForm, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['form'] = self.form_class(self.request.user)

        return context

    def form_valid(self, form):
        form.send_organization_guide()
        messages.success(self.request, _('We have sent the Organizer Guide to you by email, please check your inbox!'))
        return super().form_valid(form)


@method_decorator(user_is_team_organizer, name='dispatch')
class TeamUpdate(UpdateView):
    model = Team
    form_class = TeamForm
    success_url = reverse_lazy('studygroups_facilitator')


