from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import http

from studygroups.models import StudyGroup, Organizer


def user_is_group_facilitator(func):
    def decorated(*args, **kwargs):
        study_group_id = kwargs.get('study_group_id')
        study_group = get_object_or_404(StudyGroup, pk=study_group_id)
        if args[0].user.is_staff or args[0].user == study_group.facilitator or Organizer.objects.filter(user=args[0].user).exists():
            return func(*args, **kwargs)
        raise PermissionDenied
    return login_required(decorated)


def user_is_organizer(func):
    def decorated(*args, **kwargs):
        if args[0].user.is_staff or Organizer.objects.filter(user=args[0].user).exists():
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
