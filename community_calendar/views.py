from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import formats
from django.utils import timezone 
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django import http

from .models import Event
from .forms import EventForm
from .forms import EventModerateForm
from .decorators import user_owns_event
from .tasks import send_new_event_notification


@method_decorator(login_required, name="dispatch")
class EventCreate(CreateView):
    """ View used by organizers and facilitators """
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('studygroups_facilitator')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        # send message for staff to moderate 
        # TODO auto moderate if the user is staff
        send_new_event_notification.delay(self.object)
        messages.success(self.request, _('Your event has been added.'))
        return http.HttpResponseRedirect(self.get_success_url())


event_edit_decorators = [login_required, user_owns_event]
@method_decorator(event_edit_decorators, name="dispatch")
class EventUpdate(UpdateView):
    model = Event
    form_class = EventForm
    success_url = reverse_lazy('studygroups_facilitator')

    def form_valid(self, form):
        messages.success(self.request, _('Your event has been updated.'))
        return super().form_valid(form)


@method_decorator(event_edit_decorators, name="dispatch")
class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('studygroups_facilitator')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Your event has been deleted.'))
        return super().delete(request, *args, **kwargs)


@method_decorator(login_required, name="dispatch")
class EventModerate(UpdateView):
    model = Event
    form_class = EventModerateForm
    success_url = reverse_lazy('studygroups_facilitator')
    template_name = 'community_calendar/event_moderate.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff :
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.moderated_by = self.request.user
        self.object.moderated_at = timezone.now()
        self.object.save()
        return http.HttpResponseRedirect(self.get_success_url())
