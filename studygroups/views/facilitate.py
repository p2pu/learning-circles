from django.core.urlresolvers import reverse, reverse_lazy
from django import http
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm

from studygroups.forms import FacilitatorForm
from studygroups.models import Facilitator

import string, random

class FacilitatorSignup(CreateView):
    model = User
    form_class = FacilitatorForm
    success_url = reverse_lazy('studygroups_landing')
    #success_url = reverse_lazy('studygroups_facilitator_signup_success')
    template_name = 'studygroups/facilitator_signup.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        self.object = User.objects.create_user(
            user.username,
            user.username,
            "".join([random.choice(string.letters) for i in range(64)])
        )
        self.object.username = user.username
        self.object.first_name = user.first_name
        self.object.last_name = user.last_name
        self.object.save()
        facilitator = Facilitator(user=self.object)
        facilitator.save()

        # send password reset email to facilitator
        reset_form = PasswordResetForm({'email': self.object.email})
        if not reset_form.is_valid():
            raise Exception(reset_form.errors)
        reset_form.save(
            subject_template_name='studygroups/facilitator_created_subject.txt',
            email_template_name='studygroups/facilitator_created_email.txt',
            html_email_template_name='studygroups/facilitator_created_email.html',
            request=self.request
        )

        return http.HttpResponseRedirect(self.get_success_url())


class FacilitatorCreate(CreateView):
    model = User
    form_class = FacilitatorForm
    success_url = reverse_lazy('studygroups_organize')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.email = self.object.username
        self.object.save()
        facilitator = Facilitator(user=self.object)
        facilitator.save()
        # TODO - send password reset email to facilitator
        return http.HttpResponseRedirect(self.get_success_url())


class FacilitatorUpdate(UpdateView):
    model = User
    form_class = FacilitatorForm
    success_url = reverse_lazy('studygroups_organize')
    context_object_name = 'facilitator' # Need this to prevent the SingleObjectMixin from overriding the user context variable used by the auth system


class FacilitatorDelete(DeleteView):
    model = User
    success_url = reverse_lazy('studygroups_organize')
    template_name = 'studygroups/confirm_delete.html'
    context_object_name = 'facilitator' # Need this to prevent the SingleObjectMixin from overriding the user context variable used by the auth system


