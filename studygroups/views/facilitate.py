from django.core.urlresolvers import reverse, reverse_lazy
from django import http
from django.forms import modelform_factory
from django.views.generic.base import View, TemplateResponseMixin, ContextMixin
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from studygroups.forms import FacilitatorForm, StudyGroupForm
from studygroups.models import Facilitator, StudyGroup, Course
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
        # TODO - who does this email come from?
        reset_form = PasswordResetForm({'email': self.object.email})
        if not reset_form.is_valid():
            raise Exception(reset_form.errors)
        reset_form.save(
            subject_template_name='studygroups/facilitator_created_subject.txt',
            email_template_name='studygroups/facilitator_created_email.txt',
            html_email_template_name='studygroups/facilitator_created_email.html',
            request=self.request,
            from_email=settings.SERVER_EMAIL,
        )

        return http.HttpResponseRedirect(self.get_success_url())


class FacilitatorSignupSuccess(TemplateView):
    template_name = 'studygroups/facilitator_signup_success.html'


class FacilitatorStudyGroupCreate(CreateView):
    success_url = reverse_lazy('studygroups_facilitator')
    template_name = 'studygroups/facilitator_studygroup_form.html'
    
    def get_form_class(self):
        return modelform_factory(StudyGroup, form=StudyGroupForm, exclude=['facilitator'])

    def get_form(self, form_class=None):
        form = super(FacilitatorStudyGroupCreate, self).get_form(form_class)
        # TODO - filter courses for facilitators that are part of a team (probably move the logic to models)
        form.fields["course"].queryset = Course.objects.filter(Q(created_by=self.request.user) | Q(created_by__isnull=True)).order_by('title')
        return form

    def form_valid(self, form):
        study_group = form.save(commit=False)
        study_group.facilitator = self.request.user
        study_group.save()
        generate_all_meetings(study_group)

        context = {
            'study_group': study_group,
            'protocol': 'https',
            'domain': settings.DOMAIN,
        }
        subject = render_to_string('studygroups/learning_circle_created_subject.txt', context).strip(' \n')
        text_body = render_to_string('studygroups/learning_circle_created.txt', context)
        html_body = render_to_string('studygroups/learning_circle_created.html', context)

        notification = EmailMultiAlternatives(
            subject,
            text_body,
            settings.DEFAULT_FROM_EMAIL,
            [study_group.facilitator.email]
        )
        notification.attach_alternative(html_body, 'text/html')
        notification.send()

        messages.success(self.request, _('You created a new Learning Circle! Check your email for next steps.'))
        return http.HttpResponseRedirect(self.success_url)


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


