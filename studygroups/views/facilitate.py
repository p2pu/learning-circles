from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django import http
from django.forms import modelform_factory
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic.base import View, TemplateResponseMixin, ContextMixin
from django.views.generic.base import RedirectView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import DetailView
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from studygroups.models import Facilitator
from studygroups.models import TeamMembership
from studygroups.models import StudyGroup
from studygroups.models import StudyGroupMeeting
from studygroups.models import Course
from studygroups.models import Application
from studygroups.models import Feedback
from studygroups.models import Reminder
from studygroups.forms import MessageForm
from studygroups.forms import ApplicationForm
from studygroups.forms import StudyGroupForm
from studygroups.forms import StudyGroupMeetingForm
from studygroups.forms import FacilitatorForm
from studygroups.forms import FeedbackForm
from studygroups.models import generate_all_meetings
from studygroups.models import send_reminder
from studygroups.models import get_study_group_organizers
from studygroups.decorators import user_is_group_facilitator

import string, random


@login_required
def login_redirect(request):
    if TeamMembership.objects.filter(user=request.user, role=TeamMembership.ORGANIZER).exists():
        url = reverse('studygroups_organize')
    else:
        url = reverse('studygroups_facilitator')
    return http.HttpResponseRedirect(url)


@login_required
def facilitator(request):
    study_groups = StudyGroup.objects.active().filter(facilitator=request.user)
    current_study_groups = study_groups.filter(end_date__gt=timezone.now())
    past_study_groups = study_groups.filter(end_date__lte=timezone.now())
    context = {
        'current_study_groups': current_study_groups,
        'past_study_groups': past_study_groups,
        'today': timezone.now()
    }
    return render_to_response('studygroups/facilitator.html', context, context_instance=RequestContext(request))


@user_is_group_facilitator
def view_study_group(request, study_group_id):
    # TODO - redirect user if the study group has been deleted
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)

    context = {
        'study_group': study_group,
        'today': timezone.now()
    }
    return render_to_response('studygroups/view_study_group.html', context, context_instance=RequestContext(request))


class FacilitatorRedirectMixin(object):
    """ Redirect facilitators back to their dashboard & organizers to the study group page """

    def get_success_url(self, *args, **kwargs):
        study_group = get_object_or_404(StudyGroup, pk=self.kwargs.get('study_group_id'))
        if study_group.facilitator == self.request.user:
            return reverse_lazy('studygroups_facilitator')
        return reverse_lazy('studygroups_view_study_group', args=(self.kwargs.get('study_group_id'),))


class MeetingCreate(FacilitatorRedirectMixin, CreateView):
    model = StudyGroupMeeting
    form_class = StudyGroupMeetingForm

    def get_initial(self):
        study_group = get_object_or_404(StudyGroup, pk=self.kwargs.get('study_group_id'))
        return {
            'study_group': study_group,
        }


class MeetingUpdate(FacilitatorRedirectMixin, UpdateView):
    model = StudyGroupMeeting
    form_class = StudyGroupMeetingForm


class MeetingDelete(FacilitatorRedirectMixin, DeleteView):
    model = StudyGroupMeeting


class FeedbackDetail(FacilitatorRedirectMixin, DetailView):
    model = Feedback


class FeedbackCreate(FacilitatorRedirectMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm

    def get_initial(self):
        meeting = get_object_or_404(StudyGroupMeeting, pk=self.kwargs.get('study_group_meeting_id'))
        return {
            'study_group_meeting': meeting,
        }

    def form_valid(self, form):
        # send notification to organizers about feedback 
        to = [] #TODO should we send this to someone if the facilitators is not part of a team? - for now, don't worry, this notification is likely to be removed.
        meeting = get_object_or_404(StudyGroupMeeting, pk=self.kwargs.get('study_group_meeting_id'))
        organizers = get_study_group_organizers(meeting.study_group)
        if organizers:
            to = [o.email for o in organizers]

        context = {
            'feedback': form.save(commit=False),
            'study_group_meeting': self.get_initial()['study_group_meeting']
        }
        subject = render_to_string('studygroups/notifications/feedback-submitted-subject.txt', context).strip('\n')
        html_body = render_to_string('studygroups/notifications/feedback-submitted.html', context)
        text_body = render_to_string('studygroups/notifications/feedback-submitted.txt', context)
        notification = EmailMultiAlternatives(subject, text_body, settings.SERVER_EMAIL, to)
        notification.attach_alternative(html_body, 'text/html')
        notification.send()
        
        return super(FeedbackCreate, self).form_valid(form)


class ApplicationDelete(FacilitatorRedirectMixin, DeleteView):
    model = Application
    success_url = reverse_lazy('studygroups_facilitator')
    template_name = 'studygroups/confirm_delete.html'


class CourseCreate(CreateView):
    """ View used by organizers and facilitators """
    model = Course
    fields = [    
        'title',
        'provider',
        'link',
        'caption',
        'start_date',
        'duration',
        'time_required',
        'prerequisite',
    ]

    def form_valid(self, form):
        # courses created by staff will be global
        if self.request.user.is_staff:
            return super(CourseCreate, self).form_valid(form)
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if TeamMembership.objects.filter(user=self.request.user, role=TeamMembership.ORGANIZER).exists():
            return reverse_lazy('studygroups_organize')
        else:
            return reverse('studygroups_facilitator_studygroup_create')


## This form is used by facilitators
class StudyGroupUpdate(FacilitatorRedirectMixin, UpdateView):
    model = StudyGroup
    form_class =  modelform_factory(StudyGroup, StudyGroupForm, exclude=['facilitator'])
    pk_url_kwarg = 'study_group_id'


class StudyGroupDelete(FacilitatorRedirectMixin, DeleteView):
    # TODO Need to fix back link for confirmation page 
    model = StudyGroup
    template_name = 'studygroups/confirm_delete.html'
    pk_url_kwarg = 'study_group_id'


class StudyGroupToggleSignup(RedirectView, SingleObjectMixin):
    model = StudyGroup
    pk_url_kwarg = 'study_group_id'
    permanent = False

    def get(self, request, *args, **kwargs):
        #TODO - should be a post
        #TODO - redirect is probably not the best way to indicate success
        study_group = self.get_object()
        study_group.signup_open = not study_group.signup_open
        study_group.save()
        messages.success(self.request, _('Signup successfully changed'))
        return super(StudyGroupToggleSignup, self).get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        if self.get_object().facilitator == self.request.user:
            return reverse_lazy('studygroups_facilitator')
        return reverse_lazy('studygroups_view_study_group', args=(self.kwargs.get('study_group_id'),))


@user_is_group_facilitator
def message_send(request, study_group_id):
    # TODO - this piggy backs of Reminder, won't work of Reminder is coupled to StudyGroupMeeting
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            reminder = form.save()
            send_reminder(reminder)
            messages.success(request, 'Email successfully sent')
            url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
    else:
        form = MessageForm(initial={'study_group': study_group})

    context = {
        'study_group': study_group,
        'course': study_group.course,
        'form': form
    }
    return render_to_response('studygroups/email.html', context, context_instance=RequestContext(request))


@user_is_group_facilitator
def message_edit(request, study_group_id, message_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    reminder = get_object_or_404(Reminder, pk=message_id)
    if not reminder.sent_at == None:
        url = reverse('studygroups_facilitator')
        messages.info(request, 'Message has already been sent and cannot be edited.')
        return http.HttpResponseRedirect(url)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=reminder)
        if form.is_valid():
            reminder = form.save()
            messages.success(request, 'Message successfully edited')
            url = reverse('studygroups_view_study_group', args=(study_group_id,))
            if study_group.facilitator == request.user:
                url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
    else:
        form = MessageForm(instance=reminder)

    context = {
        'study_group': study_group,
        'course': study_group.course,
        'form': form
    }
    return render_to_response('studygroups/message_edit.html', context, context_instance=RequestContext(request))


@user_is_group_facilitator
def add_member(request, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, initial={'study_group': study_group})
        if form.is_valid():
            application = form.save(commit=False)
            if application.email and Application.objects.active().filter(email=application.email, study_group=study_group).exists():
                old_application = Application.objects.active().filter(email=application.email, study_group=study_group).first()
                application.pk = old_application.pk
                application.created_at = old_application.created_at

            if application.mobile and Application.objects.active().filter(mobile=application.mobile, study_group=study_group).exists():
                old_application = Application.objects.active().filter(mobile=application.mobile, study_group=study_group).first()
                application.pk = old_application.pk
                application.created_at = old_application.created_at

            # TODO - remove accepted_at or use accepting applications flow
            application.accepted_at = timezone.now()
            application.save()
            url = reverse('studygroups_view_study_group', args=(study_group_id,))
            if study_group.facilitator == request.user:
                url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
    else:
        form = ApplicationForm(initial={'study_group': study_group})

    context = {
        'form': form,
        'study_group': study_group,
    }
    return render_to_response('studygroups/add_member.html', context, context_instance=RequestContext(request))

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
