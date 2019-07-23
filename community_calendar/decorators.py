from django.core.exceptions import PermissionDenied

from .models import Event

from functools import wraps


def user_owns_event(f, *args, **kwargs):
    @wraps(f)
    def _check(*args, **kwargs):
        event = Event.objects.get(pk=kwargs.get('pk'))
        if event and (event.created_by == args[0].user or args[0].user.is_staff):
            return f(*args, **kwargs)
        raise PermissionDenied
    return _check

