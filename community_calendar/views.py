from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import formats
from django.utils.translation import ugettext as _
from django import http

from .models import Event
from .forms import EventForm
from .decorators import user_owns_event

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
        # moderation logic be here
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
