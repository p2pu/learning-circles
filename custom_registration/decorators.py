from django import http
from django.urls import reverse


def user_is_not_logged_in(func):
    def decorated(*args, **kwargs):
        if args[0].user.is_authenticated:
            url = reverse('studygroups_login_redirect')
            return http.HttpResponseRedirect(url)
        return func(*args, **kwargs)
    return decorated
