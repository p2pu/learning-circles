from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import http

from studygroups.models import StudyGroup, Organizer
from studygroups.models import TeamMembership
from studygroups.models import get_study_group_organizers


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


def user_is_not_logged_in(func):
    def decorated(*args, **kwargs):
        if args[0].user.is_authenticated():
            url = reverse('studygroups_login_redirect')
            return http.HttpResponseRedirect(url)
        return func(*args, **kwargs)
    return decorated
