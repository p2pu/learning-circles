from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django import http
from django import forms
from django.forms import modelform_factory, HiddenInput
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic.base import View, TemplateResponseMixin, ContextMixin
from django.views.generic.base import RedirectView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core import serializers
from django.template.defaultfilters import slugify

import json


from studygroups.models import Activity
from studygroups.models import Facilitator
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import StudyGroup
from studygroups.models import StudyGroupMeeting
from studygroups.models import Course
from studygroups.models import Application
from studygroups.models import Feedback
from studygroups.models import Reminder
from studygroups.forms import CourseForm
from studygroups.forms import ApplicationForm
from studygroups.forms import StudyGroupForm
from studygroups.forms import StudyGroupMeetingForm
from studygroups.forms import FeedbackForm
from studygroups.models import generate_all_meetings
from studygroups.models import send_reminder
from studygroups.models import get_study_group_organizers
from studygroups.decorators import user_is_group_facilitator


import string, random

def _map_to_json(sg):
    data = {
        "course": {
            "id": sg.course.pk,
            "title": sg.course.title,
            "provider": sg.course.provider,
            "link": sg.course.link
        },
        "facilitator": sg.facilitator.first_name + " " + sg.facilitator.last_name,
        "venue": sg.venue_name,
        "venue_address": sg.venue_address + ", " + sg.city,
        "city": sg.city,
        "latitude": sg.latitude,
        "longitude": sg.longitude,
        "day": sg.day(),
        "start_date": sg.start_date,
        "meeting_time": sg.meeting_time,
        "time_zone": sg.timezone_display(),
        "end_time": sg.end_time(),
        "weeks": sg.studygroupmeeting_set.active().count(),
        "url": settings.DOMAIN + reverse('studygroups_signup', args=(slugify(sg.venue_name), sg.id,)),
    }
    if sg.image:
        data["image_url"] = settings.DOMAIN + sg.image.url
    # TODO else set default image URL
    if hasattr(sg, 'next_meeting_date'):
        data["next_meeting_date"] = sg.next_meeting_date
    return data


@login_required
def login_redirect(request):
    if TeamMembership.objects.filter(user=request.user, role=TeamMembership.ORGANIZER).exists():
        team = TeamMembership.objects.get(user=request.user, role=TeamMembership.ORGANIZER).team
        url = reverse('studygroups_organize_team', args=(team.pk,))
    else:
        url = reverse('studygroups_facilitator')
    return http.HttpResponseRedirect(url)


@login_required
def facilitator(request):
    study_groups = StudyGroup.objects.active().filter(facilitator=request.user)
    current_study_groups = study_groups.filter(end_date__gt=timezone.now())
    past_study_groups = study_groups.filter(end_date__lte=timezone.now())
    team = None
    if TeamMembership.objects.filter(user=request.user).exists():
        team = TeamMembership.objects.filter(user=request.user).first().team
    invitation = TeamInvitation.objects.filter(email__iexact=request.user.email, responded_at__isnull=True).first()
    context = {
        'current_study_groups': current_study_groups,
        'past_study_groups': past_study_groups,
        'activities': Activity.objects.all().order_by('index'),
        'courses': Course.objects.filter(created_by=request.user),
        'invitation': invitation,
        'today': timezone.now(),
        'team': team
    }
    return render(request, 'studygroups/facilitator.html', context)


@user_is_group_facilitator
def view_study_group(request, study_group_id):
    # TODO - redirect user if the study group has been deleted
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)

    context = {
        'study_group': study_group,
        'today': timezone.now()
    }
    return render(request, 'studygroups/view_study_group.html', context)


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
        subject = render_to_string('studygroups/email/feedback-submitted-subject.txt', context).strip('\n')
        html_body = render_to_string('studygroups/email/feedback-submitted.html', context)
        text_body = render_to_string('studygroups/email/feedback-submitted.txt', context)
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
    form_class = CourseForm

    def get_context_data(self, **kwargs):
        context = super(CourseCreate, self).get_context_data(**kwargs)
        topics = Course.objects.active()\
                .filter(unlisted=False)\
                .exclude(topics='')\
                .values_list('topics')
        topics = [
            item.strip().lower() for sublist in topics for item in sublist[0].split(',')
        ]
        context['topics'] = list(set(topics))
        return context


    def form_valid(self, form):
        # courses created by staff will be global
        messages.success(self.request, _('Your course has been created. You can now create a learning circle using it.'))
        if self.request.user.is_staff:
            return super(CourseCreate, self).form_valid(form)
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        #if self.request.user.is_staff: #TeamMembership.objects.filter(user=self.request.user, role=TeamMembership.ORGANIZER).exists():
        #    return reverse_lazy('studygroups_organize')
        #else:
        url = reverse('studygroups_facilitator_studygroup_create')
        return url + "?course_id={}".format(self.object.id)


@method_decorator(login_required, name='dispatch')
class CourseUpdate(UpdateView):
    """ View used by organizers and facilitators """
    model = Course
    form_class = CourseForm


    def dispatch(self, request, *args, **kwargs):
        course = self.get_object()
        if not request.user.is_staff and course.created_by != request.user:
            raise PermissionDenied
        other_study_groups =  StudyGroup.objects.active().filter(course=course).exclude(facilitator=request.user)
        study_groups = StudyGroup.objects.active().filter(course=course, facilitator=request.user)
        if study_groups.count() > 1 or other_study_groups.count() > 0:
            messages.warning(request, _('This course is being used by other learning circles and cannot be edited, please create a new course to make changes'))
            url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
        return super(CourseUpdate, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(CourseUpdate, self).get_context_data(**kwargs)
        topics = Course.objects.active()\
                .filter(unlisted=False)\
                .exclude(topics='')\
                .values_list('topics')
        topics = [
            item.strip().lower() for sublist in topics for item in sublist[0].split(',')
        ]
        context['topics'] = list(set(topics))
        return context


    def form_valid(self, form):
        # courses created by staff will be global
        messages.success(self.request, _('Your course has been created. You can now create a learning circle using it.'))
        if self.request.user.is_staff:
            return super(CourseUpdate, self).form_valid(form)
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())


    def get_success_url(self):
        url = reverse('studygroups_facilitator')
        return url


## This form is used by facilitators
class StudyGroupUpdate(FacilitatorRedirectMixin, UpdateView):
    model = StudyGroup
    form_class =  StudyGroupForm
    pk_url_kwarg = 'study_group_id'

    def get_context_data(self, **kwargs):
        study_group = self.get_object()
        context = super(StudyGroupUpdate, self).get_context_data(**kwargs)
        context['hide_footer'] = True
        context['studygroup'] = study_group.id
        return context


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


@method_decorator(user_is_group_facilitator, name='dispatch')
class StudyGroupPublish(SingleObjectMixin, View):
    model = StudyGroup
    pk_url_kwarg = 'study_group_id'

    def post(self, request, *args, **kwargs):
        study_group = self.get_object()
        profile = study_group.facilitator.facilitator
        if profile.email_confirmed_at is None:
            messages.warning(self.request, _("You need to confirm your email address before you can publish a learning circle."));
        else:
            study_group.draft = False
            study_group.save()

        url = reverse_lazy('studygroups_view_study_group', args=(self.kwargs.get('study_group_id'),))
        if self.get_object().facilitator == self.request.user:
            url = reverse_lazy('studygroups_facilitator')
        return http.HttpResponseRedirect(url)


@user_is_group_facilitator
def message_send(request, study_group_id):
    # TODO - this piggy backs of Reminder, won't work of Reminder is coupled to StudyGroupMeeting
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    form_class =  modelform_factory(Reminder, exclude=['study_group_meeting', 'created_at', 'sent_at', 'sms_body'], widgets={'study_group': HiddenInput})

    needs_mobile = study_group.application_set.active().exclude(mobile='').count() > 0
    if needs_mobile:
        form_class = modelform_factory(Reminder, exclude=['study_group_meeting', 'created_at', 'sent_at'], widgets={'study_group': HiddenInput})

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            reminder = form.save()
            send_reminder(reminder)
            messages.success(request, 'Email successfully sent')
            url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
    else:
        form = form_class(initial={'study_group': study_group})

    context = {
        'study_group': study_group,
        'course': study_group.course,
        'form': form
    }
    return render(request, 'studygroups/email.html', context)


@user_is_group_facilitator
def message_edit(request, study_group_id, message_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    reminder = get_object_or_404(Reminder, pk=message_id)
    if not reminder.sent_at == None:
        url = reverse('studygroups_facilitator')
        messages.info(request, 'Message has already been sent and cannot be edited.')
        return http.HttpResponseRedirect(url)

    form_class =  modelform_factory(Reminder, exclude=['study_group_meeting', 'created_at', 'sent_at', 'sms_body'], widgets={'study_group': HiddenInput})
    needs_mobile = study_group.application_set.active().exclude(mobile='').count() > 0
    if needs_mobile:
        form_class = modelform_factory(Reminder, exclude=['study_group_meeting', 'created_at', 'sent_at'], widgets={'study_group': HiddenInput})

    if request.method == 'POST':
        form = form_class(request.POST, instance=reminder)
        if form.is_valid():
            reminder = form.save()
            messages.success(request, 'Message successfully edited')
            url = reverse('studygroups_view_study_group', args=(study_group_id,))
            if study_group.facilitator == request.user:
                url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
    else:
        form = form_class(instance=reminder)

    context = {
        'study_group': study_group,
        'course': study_group.course,
        'form': form
    }
    return render(request, 'studygroups/message_edit.html', context)


@user_is_group_facilitator
def add_member(request, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)

    # only require name, email and/or mobile
    form_class =  modelform_factory(Application, fields=['study_group', 'name', 'email', 'mobile'], widgets={'study_group': HiddenInput})

    if request.method == 'POST':
        form = form_class(request.POST, initial={'study_group': study_group})
        if form.is_valid():
            url = reverse('studygroups_view_study_group', args=(study_group_id,))
            application = form.save(commit=False)
            if application.email and Application.objects.active().filter(email__iexact=application.email, study_group=study_group).exists():
                messages.warning(request, _('User with the given email address already signed up.'))
            elif application.mobile and Application.objects.active().filter(mobile=application.mobile, study_group=study_group).exists():
                messages.warning(request, _('User with the given mobile number already signed up.'))
            else:
                # TODO - remove accepted_at or use accepting applications flow
                application.accepted_at = timezone.now()
                application.save()
            if study_group.facilitator == request.user:
                url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
    else:
        form = form_class(initial={'study_group': study_group})

    context = {
        'form': form,
        'study_group': study_group,
    }
    return render(request, 'studygroups/add_member.html', context)

class FacilitatorStudyGroupCreate(CreateView):
    success_url = reverse_lazy('studygroups_facilitator')
    template_name = 'studygroups/facilitator_studygroup_form.html'
    form_class = StudyGroupForm

    def get_initial(self):
        initial = {}
        course_id = self.request.GET.get('course_id', None)
        if course_id:
            initial['course'] = get_object_or_404(Course, pk=course_id)
        return initial

    def form_valid(self, form):
        study_group = form.save(commit=False)
        study_group.facilitator = self.request.user
        study_group.save()
        generate_all_meetings(study_group)
        messages.success(self.request, _('You created a new Learning Circle! Check your email for next steps.'))
        return http.HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super(FacilitatorStudyGroupCreate, self).get_context_data(**kwargs)
        context['hide_footer'] = True
        return context

class FacilitatorStudyGroupPublished(TemplateView):
    template_name = 'studygroups/facilitator_studygroup_published.html'

class FacilitatorStudyGroupSaved(TemplateView):
    template_name = 'studygroups/facilitator_studygroup_saved.html'


class InvitationConfirm(FormView):
    form_class = forms.Form
    template_name = 'studygroups/invitation_confirm.html'
    success_url = reverse_lazy('studygroups_facilitator')

    def get(self, request, *args, **kwargs):
        invitation = TeamInvitation.objects.filter(
                email__iexact=self.request.user.email,
                responded_at__isnull=True).first()
        if invitation is None:
            messages.warning(self.request, _('No team invitations found'))
            return http.HttpResponseRedirect(reverse('studygroups_facilitator'))

        return super(InvitationConfirm, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InvitationConfirm, self).get_context_data(**kwargs)
        invitation = TeamInvitation.objects.filter(
                email__iexact=self.request.user.email,
                responded_at__isnull=True).first()
        team_membership = TeamMembership.objects.filter(user=self.request.user).first()
        context['invitation'] = invitation
        context['team_membership'] = team_membership
        return context

    def form_valid(self, form):
        # Update invitation
        invitation = TeamInvitation.objects.filter(email__iexact=self.request.user.email, responded_at__isnull=True).first()
        current_membership_qs = TeamMembership.objects.filter(user=self.request.user)
        if current_membership_qs.filter(role=TeamMembership.ORGANIZER).exists() and self.request.POST['response'] == 'yes':
            messages.warning(self.request, _('You are currently the organizer of another team and cannot join this team.'))
            return http.HttpResponseRedirect(reverse('studygroups_facilitator'))
        invitation.responded_at = timezone.now()
        invitation.joined = self.request.POST['response'] == 'yes'
        invitation.save()
        if invitation.joined is True:
            if current_membership_qs.exists():
                current_membership_qs.delete()
            TeamMembership.objects.create(team=invitation.team, user=self.request.user, role=invitation.role)

        return super(InvitationConfirm, self).form_valid(form)
