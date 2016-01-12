from django.core.urlresolvers import reverse, reverse_lazy
from django import http
from django.forms import modelform_factory
from django.views.generic.base import View, TemplateResponseMixin, ContextMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.utils.translation import ugettext as _

from studygroups.forms import FacilitatorForm, StudyGroupForm
from studygroups.models import Facilitator, StudyGroup, Location
from studygroups.models import generate_all_meetings

import string, random, datetime

class FacilitatorSignup(CreateView):
    model = User
    form_class = FacilitatorForm
    success_url = reverse_lazy('studygroups_facilitator_signup_success')
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


class FacilitatorSignupSuccess(TemplateView):
    template_name = 'studygroups/facilitator_signup_success.html'


class FacilitatorStudyGroupCreate(View, TemplateResponseMixin, ContextMixin):
    success_url = reverse_lazy('studygroups_facilitator')
    template_name = 'studygroups/facilitator_studygroup_form.html'
    location_fields = ['name', 'address', 'contact_name', 'contact', 'link', 'image']

    def get_location_form_class(self):
        return modelform_factory(Location, fields=self.location_fields)
    
    def get_studygroup_form_class(self):
        return modelform_factory(StudyGroup, form=StudyGroupForm, exclude=['location', 'facilitator'])

    def get(self, request, *args, **kwargs):
        location_form_cls = self.get_location_form_class()
        location_form = location_form_cls(prefix='location_')
        studygroup_form = self.get_studygroup_form_class()()
        return self.render_to_response(self.get_context_data(location_form=location_form, studygroup_form=studygroup_form))

    def post(self, request, *args, **kwargs):
        location_form_cls = self.get_location_form_class()
        location_form = location_form_cls(self.request.POST, self.request.FILES, prefix='location_')
        studygroup_form = self.get_studygroup_form_class()(self.request.POST)
        if location_form.is_valid() and studygroup_form.is_valid():
            study_group = studygroup_form.save(commit=False)
            location = location_form.save()
            study_group.facilitator = request.user
            study_group.location = location
            study_group.end_date = study_group.start_date + datetime.timedelta(weeks=studygroup_form.cleaned_data['weeks'] - 1) # TODO - consider doing this in the form
            study_group.save()
            generate_all_meetings(study_group)
            messages.success(request, _('Learning circle successfully created.'))
            return http.HttpResponseRedirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(location_form=location_form, studygroup_form=studygroup_form))


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


