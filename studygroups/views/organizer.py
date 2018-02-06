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
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic import ListView

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import Facilitator
from studygroups.models import StudyGroupMeeting
from studygroups.models import report_data
from studygroups.models import generate_all_meetings
from studygroups.models import Team
from studygroups.models import get_team_users
from studygroups.models import get_user_team
from studygroups.models import send_team_invitation_email
from studygroups.decorators import user_is_organizer
from studygroups.decorators import user_is_team_organizer


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
    facilitators = Facilitator.objects.all()  # TODO rather use User model
    courses = []  # TODO Remove courses until we implement course selection for teams
    team = None
    invitations = []

    active_study_groups = study_groups.filter(
        id__in=StudyGroupMeeting.objects.active().filter(meeting_date__gte=two_weeks_ago).values('study_group')
    )
    meetings = StudyGroupMeeting.objects.active()\
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

    members = team.teammembership_set.values('user')
    team_users = User.objects.filter(pk__in=members)
    study_groups = StudyGroup.objects.published().filter(facilitator__in=team_users)
    facilitators = Facilitator.objects.filter(user__in=team_users)
    invitations = TeamInvitation.objects.filter(team=team, responded_at__isnull=True)
    active_study_groups = study_groups.filter(
        id__in=StudyGroupMeeting.objects.active().filter(meeting_date__gte=two_weeks_ago).values('study_group')
    )
    meetings = StudyGroupMeeting.objects.active()\
        .filter(study_group__in=study_groups, meeting_date__gte=two_weeks_ago)\
        .exclude(meeting_date__gte=two_weeks)

    context = {
        'team': team,
        'meetings': meetings,
        'study_groups': study_groups,
        'active_study_groups': active_study_groups,
        'facilitators': facilitators,
        'invitations': invitations,
        'today': timezone.now(),
    }
    return render(request, 'studygroups/organize.html', context)


class StudyGroupList(ListView):
    model = StudyGroup

    def get_queryset(self):
        study_groups = StudyGroup.objects.published()
        if not self.request.user.is_staff:
            team_users = get_team_users(self.request.user)
            study_groups = study_groups.filter(facilitator__in=team_users)
        return study_groups


class StudyGroupMeetingList(ListView):
    model = StudyGroupMeeting

    def get_queryset(self):
        study_groups = StudyGroup.objects.published()
        if not self.request.user.is_staff:
            team_users = get_team_users(self.request.user)
            study_groups = study_groups.filter(facilitator__in=team_users)

        meetings = StudyGroupMeeting.objects.active().filter(study_group__in=study_groups)
        return meetings


class TeamMembershipDelete(DeleteView):
    model = TeamMembership
    success_url = reverse_lazy('studygroups_organize')
    template_name = 'studygroups/confirm_delete_membership.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = TeamMembership.objects
        return queryset.get(user_id=self.kwargs.get('user_id'), team_id=self.kwargs.get('team_id'))


class CourseDelete(DeleteView):
    model = Course
    success_url = reverse_lazy('studygroups_organize')
    template_name = 'studygroups/confirm_delete.html'


class TeamInvitationCreate(View):

    @method_decorator(csrf_exempt)
    @method_decorator(user_is_team_organizer)
    def dispatch(self, *args, **kwargs):
        return super(TeamInvitationCreate, self).dispatch(*args, **kwargs)

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
        if TeamMembership.objects.filter(team=team, user__email__iexact=email).exists():
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


@user_is_organizer
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
    membership = TeamMembership.objects.filter(user=request.user, role=TeamMembership.ORGANIZER).first()
    if membership:
        team = membership.team

    context.update(report_data(start_time, end_time, team))
    return render(request, 'studygroups/email/weekly-update.html', context)
