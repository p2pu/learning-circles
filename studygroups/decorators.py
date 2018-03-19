from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django import http
from django.utils.translation import ugettext as _

from studygroups.models import StudyGroup, Organizer
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import get_study_group_organizers


def study_group_is_published(func):
    def decorated(*args, **kwargs):
        study_group_id = kwargs.get('study_group_id')
        study_group = get_object_or_404(StudyGroup, pk=study_group_id)
        if study_group.draft == True:
            messages.warning(args[0], _("Your learning circle is still a draft and should be published first."));
            url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
        return func(*args, **kwargs)
    return decorated


def user_is_group_facilitator(func):
    def decorated(*args, **kwargs):
        study_group_id = kwargs.get('study_group_id')
        # TODO this logic should be in the model
        study_group = get_object_or_404(StudyGroup, pk=study_group_id)
        if args[0].user.is_staff \
                or args[0].user == study_group.facilitator \
                or TeamMembership.objects.filter(user=args[0].user, role=TeamMembership.ORGANIZER).exists() and args[0].user in get_study_group_organizers(study_group):
            return func(*args, **kwargs)
        raise PermissionDenied
    return login_required(decorated)


def user_is_organizer(func):
    def decorated(*args, **kwargs):
        # TODO this logic should be in the model
        if args[0].user.is_staff or TeamMembership.objects.filter(user=args[0].user, role=TeamMembership.ORGANIZER).exists():
            return func(*args, **kwargs)
        raise PermissionDenied
    return login_required(decorated)


def user_is_team_organizer(func):
    def decorated(*args, **kwargs):
        team_id = kwargs.get('team_id')
        team = Team.objects.filter(pk=team_id).first()
        if team is None:
            raise PermissionDenied
        if args[0].user.is_staff or TeamMembership.objects.filter(user=args[0].user, team=team, role=TeamMembership.ORGANIZER).exists():
            return func(*args, **kwargs)
        raise PermissionDenied
    return login_required(decorated)


def user_is_staff(func):
    def decorated(*args, **kwargs):
        if args[0].user.is_staff is False:
            raise PermissionDenied
        return func(*args, **kwargs)
    return login_required(decorated)
