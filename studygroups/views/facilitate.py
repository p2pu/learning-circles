from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django import http
from django import forms
from django.forms import modelform_factory, HiddenInput
from django.forms import modelformset_factory
from django.forms import inlineformset_factory
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import View
from django.views.generic.base import RedirectView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import DetailView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

import re
import json
import datetime
import logging

from tinymce.widgets import TinyMCE

from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import StudyGroup
from studygroups.models import Facilitator
from studygroups.models import Meeting
from studygroups.models import Course
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.forms import ApplicationInlineForm
from studygroups.forms import CourseForm
from studygroups.forms import StudyGroupForm
from studygroups.forms import MeetingForm
from studygroups.tasks import send_reminder
from studygroups.models import generate_meetings_from_dates
from studygroups.models import generate_all_meeting_dates
from studygroups.models import get_study_group_organizers
from studygroups.decorators import user_is_group_facilitator
from studygroups.decorators import user_is_team_member
from studygroups.decorators import study_group_is_published
from studygroups.charts import OverallRatingBarChart
from studygroups.discourse import create_discourse_topic
from studygroups.utils import render_to_string_ctx
from studygroups.views.api import serialize_course
from studygroups.models.team import eligible_team_by_email_domain
from studygroups.models import weekly_update_data

logger = logging.getLogger(__name__)

@login_required
def login_redirect(request):
    url = reverse('studygroups_facilitator')
    return http.HttpResponseRedirect(url)


@user_is_group_facilitator
def view_study_group(request, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    if study_group.deleted_at:
        raise http.Http404(_("Learning circle does not exist."))

    dashboard_url = reverse('studygroups_facilitator')
    remaining_surveys = study_group.application_set.active().exclude(id__in=study_group.learnersurveyresponse_set.values('learner_id'))

    context = {
        'study_group': study_group,
        'today': timezone.now(),
        'dashboard_url': dashboard_url,
        'remaining_surveys': remaining_surveys,
    }
    meeting_number = request.GET.get('meeting')
    rating = request.GET.get('rating')
    if meeting_number and rating:
        context['expand_meeting'] = meeting_number
        context['meeting_rating'] = rating

    return render(request, 'studygroups/view_study_group.html', context)


class FacilitatorRedirectMixin(object):
    """ Redirect to the study group page """

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('studygroups_view_study_group', args=(self.kwargs.get('study_group_id'),))


@method_decorator(user_is_group_facilitator, name="dispatch")
class MeetingCreate(FacilitatorRedirectMixin, CreateView):
    model = Meeting
    form_class = MeetingForm

    def get_initial(self):
        study_group_id = self.kwargs.get('study_group_id')
        study_group = get_object_or_404(StudyGroup, pk=study_group_id)
        return {
            'study_group': study_group,
            'meeting_time': study_group.meeting_time,
        }


@method_decorator(user_is_group_facilitator, name="dispatch")
class MeetingUpdate(FacilitatorRedirectMixin, UpdateView):
    model = Meeting
    form_class = MeetingForm


@method_decorator(user_is_group_facilitator, name="dispatch")
class MeetingDelete(FacilitatorRedirectMixin, DeleteView):
    model = Meeting


@method_decorator(user_is_group_facilitator, name="dispatch")
class ApplicationUpdate(FacilitatorRedirectMixin, UpdateView):
    model = Application
    form_class =  modelform_factory(Application, fields=['study_group', 'name', 'email', 'mobile'], widgets={'study_group': HiddenInput})
    template_name = 'studygroups/add_learner.html'


@method_decorator(user_is_group_facilitator, name="dispatch")
class ApplicationDelete(FacilitatorRedirectMixin, DeleteView):
    model = Application
    success_url = reverse_lazy('studygroups_facilitator')
    template_name = 'studygroups/confirm_delete.html'


@method_decorator(user_is_group_facilitator, name='dispatch')
class MessageView(DetailView):
    model = Reminder
    template_name = 'studygroups/message_view.html'
    context_object_name = 'message'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = context['message']
        if message.study_group_id != int(self.kwargs.get('study_group_id')):
            raise PermissionDenied
        message.email_body = re.sub(r'RSVP_YES_LINK', '#', message.email_body)
        message.email_body = re.sub(r'RSVP_NO_LINK', '#', message.email_body)
        message.email_body = re.sub(r'UNSUBSCRIBE_LINK', '#', message.email_body)
        return context


class CoursePage(DetailView):
    model = Course
    template_name = 'studygroups/course_page.html'
    context_object_name = 'course'

    def get_queryset(self):
        return super().get_queryset().active()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usage = StudyGroup.objects.filter(course=self.object.id).count()
        rating_step_counts = json.loads(self.object.rating_step_counts)
        similar_courses = [ serialize_course(course) for course in self.object.similar_courses()]

        context['usage'] = usage
        context['rating_counts_chart'] = OverallRatingBarChart(rating_step_counts).generate()
        context['rating_step_counts'] = rating_step_counts
        context['similar_courses'] = json.dumps(similar_courses, cls=DjangoJSONEncoder)

        return context


def generate_course_discourse_topic(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if course.discourse_topic_url:
        return http.HttpResponseRedirect(course.discourse_topic_url)

    post_title = "{} ({})".format(course.title, course.provider)
    post_category = settings.DISCOURSE_COURSES_AND_TOPICS_CATEGORY_ID
    post_raw = "{}".format(course.discourse_topic_default_body())

    try:
        response_json = create_discourse_topic(post_title, post_category, post_raw)
        topic_slug = response_json.get('topic_slug', None)
        topic_id = response_json.get('topic_id', None)
        topic_url = "{}/t/{}/{}".format(settings.DISCOURSE_BASE_URL, topic_slug, topic_id)
        course.discourse_topic_url = topic_url
        course.save()

        return http.HttpResponseRedirect(topic_url)

    except:
        courses_and_topics_category_url = "{}/c/learning-circles/courses-and-topics".format(settings.DISCOURSE_BASE_URL)
        return http.HttpResponseRedirect(courses_and_topics_category_url)


@method_decorator(login_required, name="dispatch")
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
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        messages.success(self.request, _('Your course has been added. You can now create a learning circle using it.'))
        return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
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
        other_study_groups =  StudyGroup.objects.active().filter(course=course).exclude(facilitator=request.user) # TODO
        study_groups = StudyGroup.objects.active().filter(course=course, facilitator=request.user) # TODO
        if study_groups.count() > 1 or other_study_groups.count() > 0:
            messages.warning(request, _('This course is being used by other learning circles and cannot be edited, please create a new course to make changes'))
            url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
        return super().dispatch(request, *args, **kwargs)

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


@method_decorator(ensure_csrf_cookie, name='dispatch')
class StudyGroupCreate(TemplateView):
    template_name = 'studygroups/studygroup_form.html'

    def get_context_data(self, **kwargs):
        context = super(StudyGroupCreate, self).get_context_data(**kwargs)
        context['RECAPTCHA_SITE_KEY'] = settings.RECAPTCHA_SITE_KEY # required for inline signup
        context['hide_footer'] = True
        context['team'] = []
        if TeamMembership.objects.active().filter(user=self.request.user).exists():
            team = TeamMembership.objects.active().filter(user=self.request.user).get().team
            context['team'] = [t.to_json() for t in team.teammembership_set.active()]
        return context


class StudyGroupCreateLegacy(CreateView):
    template_name = 'studygroups/studygroup_form_legacy.html'
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
        Facilitator.obects.create(user=self.request.user, study_group=study_group)
        meeting_dates = generate_all_meeting_dates(
            study_group.start_date, study_group.meeting_time, form.cleaned_data['weeks']
        )
        generate_meetings_from_dates(study_group, meeting_dates)

        messages.success(self.request, _('You created a new learning circle! Check your email for next steps.'))
        success_url = reverse_lazy('studygroups_view_study_group', args=(study_group.id,))
        return http.HttpResponseRedirect(success_url)


@method_decorator(user_is_group_facilitator, name="dispatch")
class StudyGroupUpdate(SingleObjectMixin, TemplateView):
    model = StudyGroup
    pk_url_kwarg = 'study_group_id'
    template_name = 'studygroups/studygroup_form.html'

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['meetings'] = [m.to_json() for m in self.object.meeting_set.active()]
        context['facilitators'] = [f.user_id for f in self.object.cofacilitators.all()]
        # TODO - only do this if 
        # a) the currently authenticated user is in a team 
        # or b) if it's a super user and the learning circle is part of a team
        if self.request.user.is_staff and self.object.team or TeamMembership.objects.active().filter(user=self.request.user).exists():
            context['team'] = [t.to_json() for t in self.object.team.teammembership_set.active()]
        context['hide_footer'] = True
        if Reminder.objects.filter(study_group=self.object, edited_by_facilitator=True, sent_at__isnull=True).exists():
            context['reminders_edited'] = True
            messages.warning(self.request, _('You have edited meeting reminders for meetings in the future. Update the learning circle description or venue information will cause the reminders to be regenerated and your updates to be lost'))
        return context


@method_decorator(user_is_group_facilitator, name="dispatch")
class StudyGroupUpdateLegacy(FacilitatorRedirectMixin, UpdateView):
    model = StudyGroup
    form_class =  StudyGroupForm
    pk_url_kwarg = 'study_group_id'
    template_name = 'studygroups/studygroup_form_legacy.html'

    def form_valid(self, form):
        return_value = super().form_valid(form)
        if form.date_changed and self.object.draft == False:
            meeting_dates = generate_all_meeting_dates(self.object.start_date, self.object.meeting_time, form.cleaned_data.get('weeks'))
            generate_meetings_from_dates(self.object, meeting_dates)
        return return_value


@method_decorator(user_is_group_facilitator, name="dispatch")
class StudyGroupDelete(DeleteView):
    model = StudyGroup
    template_name = 'studygroups/confirm_delete.html'
    pk_url_kwarg = 'study_group_id'
    context_object_name = 'study_group'
    success_url = reverse_lazy('studygroups_facilitator')


@method_decorator(user_is_group_facilitator, name="dispatch")
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
        return reverse_lazy('studygroups_view_study_group', args=(self.kwargs.get('study_group_id'),))


@method_decorator(user_is_group_facilitator, name='dispatch')
class StudyGroupPublish(SingleObjectMixin, View):
    model = StudyGroup
    pk_url_kwarg = 'study_group_id'

    def post(self, request, *args, **kwargs):
        study_group = self.get_object()
        profile = study_group.facilitator.profile # TODO
        if profile.email_confirmed_at is None:
            messages.warning(self.request, _("You need to confirm your email address before you can publish a learning circle."));
        else:
            messages.success(self.request, _("Your learning circle has been published."));
            study_group.draft = False
            study_group.save()
            # TODO this is temporary to still allow drafts created before to be published. This could also be replaced with a data migration that generates the meetings
            if study_group.meeting_set.active().count() == 0:
                meeting_dates = generate_all_meeting_dates(study_group.start_date, study_group.meeting_time)
                generate_meetings_from_dates(study_group, meeting_dates)

        url = reverse_lazy('studygroups_view_study_group', args=(self.kwargs.get('study_group_id'),))
        return http.HttpResponseRedirect(url)


@method_decorator(user_is_group_facilitator, name="dispatch")
class StudyGroupDidNotHappen(SingleObjectMixin, View):
    model = StudyGroup
    pk_url_kwarg = 'study_group_id'

    def post(self, request, *args, **kwargs):
        study_group = self.get_object()
        study_group.did_not_happen = True
        study_group.save()
        url = reverse_lazy('studygroups_view_study_group', args=(self.kwargs.get('study_group_id'),))
        return http.HttpResponseRedirect(url)

    def get(self, request, *args, **kwargs):
        context = {
            'study_group': self.get_object(),
        }
        return render(request, 'studygroups/confirm_did_not_happen.html', context)


@user_is_group_facilitator
@study_group_is_published
def message_send(request, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)

    widgets = {
        'email_body': TinyMCE(),
        'study_group': forms.HiddenInput
    }
    fields = ['study_group', 'email_subject', 'email_body']
    needs_mobile = study_group.application_set.active().exclude(mobile='').count() > 0
    if needs_mobile:
        fields += ['sms_body']
    form_class =  modelform_factory(Reminder, fields=fields, widgets=widgets)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            reminder = form.save()
            send_reminder(reminder)
            messages.success(request, 'Email successfully sent')
            url = reverse('studygroups_view_study_group', args=(study_group_id,))
            return http.HttpResponseRedirect(url)
    else:
        form = form_class(initial={'study_group': study_group})

    context = {
        'study_group': study_group,
        'course': study_group.course,
        'form': form
    }
    return render(request, 'studygroups/adhoc_message_form.html', context)


@user_is_group_facilitator
def message_edit(request, study_group_id, message_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    reminder = get_object_or_404(Reminder, pk=message_id)
    # dont try to edit someone elses reminder?
    if reminder.study_group != study_group:
        raise PermissionDenied
    url = reverse('studygroups_view_study_group', args=(study_group_id,))
    if not reminder.sent_at == None:
        messages.info(request, 'Message has already been sent and cannot be edited.')
        return http.HttpResponseRedirect(url)

    widgets = {
        'email_body': TinyMCE(),
        'study_group': forms.HiddenInput
    }
    fields = ['study_group', 'email_subject', 'email_body', 'sms_body']
    form_class =  modelform_factory(Reminder, fields=fields, widgets=widgets)

    if request.method == 'POST':
        form = form_class(request.POST, instance=reminder)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.edited_by_facilitator = True
            reminder.save()
            messages.success(request, 'Message successfully edited')
            return http.HttpResponseRedirect(url)
    else:
        form = form_class(instance=reminder)

    context = {
        'study_group': study_group,
        'course': study_group.course,
        'form': form
    }
    return render(request, 'studygroups/message_edit.html', context)


@method_decorator(user_is_group_facilitator, name="dispatch")
class ReminderDelete(DeleteView):
    model = Reminder

    def __todo__(self):
        # Remove the reminder
        # Indicate that this reminder has been deleted
        # use that indication in template for messaging on manage page
        # check value in other places when updating reminders
        pass


@method_decorator(user_is_group_facilitator, name="dispatch")
class RemiderRegenerate(UpdateView):
    model = Meeting
    def __todo__(self):
        # Regenerate the reminder
        # If it was manually deleted before, unset that
        pass


@method_decorator(user_is_group_facilitator, name='dispatch')
class MeetingRecap(CreateView):
    model = Reminder
    template_name = 'studygroups/meeting_recap_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meeting'] = get_object_or_404(Meeting, pk=self.kwargs.get('pk'))
        return context

    def get_form_class(self):
        study_group = get_object_or_404(StudyGroup, pk=self.kwargs.get('study_group_id'))
        fields = ['study_group', 'email_subject', 'email_body']
        needs_mobile = study_group.application_set.active().exclude(mobile='').count() > 0
        if needs_mobile:
            fields += ['sms_body']
        widgets = {
            'email_body': TinyMCE(),
            'study_group': forms.HiddenInput
        }
        return modelform_factory(Reminder, fields=fields, widgets=widgets)

    def get_initial(self):
        study_group_id = self.kwargs.get('study_group_id')
        study_group = get_object_or_404(StudyGroup, pk=study_group_id)
        return {
            'study_group': study_group,
        }

    def form_valid(self, form):
        study_group = get_object_or_404(StudyGroup, pk=self.kwargs.get('study_group_id'))
        meeting = get_object_or_404(Meeting, pk=self.kwargs.get('pk'))
        if meeting.study_group.pk != study_group.pk:
            raise PermissionDenied
        recap = form.save()
        meeting.recap = recap
        meeting.save()
        send_reminder(recap)
        messages.success(self.request, 'Follow up message has been sent')

        url = reverse_lazy('studygroups_view_study_group', args=(self.kwargs.get('study_group_id'),))
        return http.HttpResponseRedirect(url)


@method_decorator(user_is_group_facilitator, name='dispatch')
class MeetingRecapDismiss(SingleObjectMixin, View):
    model = Meeting
 
    def post(self, request, *args, **kwargs):
        meeting = self.get_object()
        # annoying that kwarg is a string
        if str(meeting.study_group.id) != kwargs.get('study_group_id'):
            raise PermissionDenied

        meeting.recap_dismissed = True
        meeting.save()

        url = reverse_lazy('studygroups_view_study_group', args=(self.kwargs.get('study_group_id'),))
        return http.HttpResponseRedirect(url)


@user_is_group_facilitator
@study_group_is_published
def add_learner(request, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)

    # only require name, email and/or mobile
    form_class =  modelform_factory(Application, form=ApplicationInlineForm)

    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            url = reverse('studygroups_view_study_group', args=(study_group_id,))
            application = form.save(commit=False)
            application.study_group = study_group
            if application.email and Application.objects.active().filter(email__iexact=application.email, study_group=study_group).exists():
                messages.warning(request, _('User with the given email address already signed up.'))
            elif application.mobile and Application.objects.active().filter(mobile=application.mobile, study_group=study_group).exists():
                messages.warning(request, _('User with the given mobile number already signed up.'))
            else:
                # TODO - remove accepted_at or use accepting applications flow
                application.accepted_at = timezone.now()
                application.save()
            return http.HttpResponseRedirect(url)
    else:
        form = form_class(initial={'study_group': study_group})

    context = {
        'form': form,
        'study_group': study_group,
    }
    return render(request, 'studygroups/add_learner.html', context)


@method_decorator([user_is_group_facilitator, study_group_is_published], name='dispatch')
class ApplicationCreateMultiple(FormView):
    template_name = 'studygroups/add_learners.html'
    form_class = modelformset_factory(
        Application,
        form=ApplicationInlineForm,
        extra=5
    )
    success_url = reverse_lazy('studygroups_facilitator')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        study_group_id = self.kwargs.get('study_group_id')
        context['study_group'] = get_object_or_404(StudyGroup, pk=study_group_id)
        return context

    def get_form(self):
        queryset = Application.objects.none()
        return self.form_class(queryset=queryset, **self.get_form_kwargs())

    def form_valid(self, form):
        study_group_id = self.kwargs.get('study_group_id')
        study_group = get_object_or_404(StudyGroup, pk=study_group_id)
        applications = form.save(commit=False)
        for application in applications:
            if application.email and Application.objects.active().filter(email__iexact=application.email, study_group=study_group).exists():
                messages.warning(self.request, _(f'A learner with the email address {application.email} has already signed up.'))
            elif application.mobile and Application.objects.active().filter(mobile=application.mobile, study_group=study_group).exists():
                messages.warning(self.request, _(f'A learner with the mobile number {application.mobile} has already signed up.'))
            else:
                application.study_group = study_group
                application.save()

        url = reverse('studygroups_view_study_group', args=(study_group_id,))
        return http.HttpResponseRedirect(url)


@method_decorator(login_required, name='dispatch')
class InvitationConfirm(FormView):
    form_class = forms.Form
    template_name = 'studygroups/invitation_confirm.html'
    success_url = reverse_lazy('studygroups_facilitator')

    def get_team_from_token(self, token):
        if token is None:
            return None

        return Team.objects.filter(invitation_token=token).first()

    def get_invitation_from_id(self, invitation_id):
        if invitation_id is None:
            return None

        return TeamInvitation.objects.filter(id=invitation_id).get()

    def get(self, request, *args, **kwargs):
        team_from_token = self.get_team_from_token(kwargs.get('token'))
        eligible_team = eligible_team_by_email_domain(self.request.user)
        invitation = TeamInvitation.objects.filter(
                email__iexact=self.request.user.email,
                responded_at__isnull=True).first()

        # if no invitation and no token and no matching domain
        if invitation is None and team_from_token is None and eligible_team is None:
            messages.warning(self.request, _('No team invitations found'))
            return http.HttpResponseRedirect(reverse('studygroups_facilitator'))

        return super(InvitationConfirm, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_membership = TeamMembership.objects.active().filter(user=self.request.user).first()
        context['team_membership'] = team_membership

        # if there's a token, get team from the token
        team_from_token = self.get_team_from_token(self.kwargs.get('token'))
        if team_from_token:
            context['team'] = team_from_token
            return context

        # if there's an invitation, get the team from the invitation
        invitation_id = self.kwargs.get('invitation_id')
        invitation = self.get_invitation_from_id(invitation_id)

        if invitation:
            context['team'] = invitation.team
            return context

        # otherwise use team with matching email
        team = eligible_team_by_email_domain(self.request.user)
        context['team'] = team
        return context

    def form_valid(self, form):
        invitation_confirmed = self.request.POST['response'] == 'yes'
        user = self.request.user
        default_role = TeamMembership.MEMBER
        new_membership = None
        current_membership_qs = TeamMembership.objects.active().filter(user=user)

        # if you're currently the only organizer for a team, you can't join any other teams
        if invitation_confirmed and current_membership_qs.filter(role=TeamMembership.ORGANIZER).exists():
            messages.warning(self.request, _('You are currently the organizer of another team and cannot join this team.'))
            return http.HttpResponseRedirect(reverse('studygroups_facilitator'))

        # add to team by token
        token = self.kwargs.get('token')
        team_from_token = self.get_team_from_token(token)
        if team_from_token:
            if invitation_confirmed:
                current_membership_qs.delete()
                pending_invitations = TeamInvitation.objects.filter(email__iexact=user.email, responded_at__isnull=True)
                pending_invitations.delete()
                new_membership = TeamMembership.objects.create(team=team_from_token, user=user, role=default_role)
                messages.success(self.request, _('Welcome to the team! You are now a part of {}.'.format(new_membership.team.name)))
                return super(InvitationConfirm, self).form_valid(form)
            else:
                return super(InvitationConfirm, self).form_valid(form)

        # add to team by invitation
        invitation_id = self.kwargs.get('invitation_id')
        invitation = self.get_invitation_from_id(invitation_id)

        if invitation:
            invitation.responded_at = timezone.now()
            invitation.joined = invitation_confirmed
            invitation.save()

            if invitation_confirmed:
                current_membership_qs.delete()
                pending_invitations = TeamInvitation.objects.filter(email__iexact=user.email, responded_at__isnull=True)
                pending_invitations.delete()
                new_membership = TeamMembership.objects.create(team=invitation.team, user=user, role=invitation.role)
                messages.success(self.request, _('Welcome to the team! You are now a part of {}.'.format(new_membership.team.name)))
                return super(InvitationConfirm, self).form_valid(form)
            else:
                return super(InvitationConfirm, self).form_valid(form)

        # add to team by matching email
        eligible_team = eligible_team_by_email_domain(user)
        if eligible_team:
            if invitation_confirmed:
                current_membership_qs.delete()
                pending_invitations = TeamInvitation.objects.filter(email__iexact=user.email, responded_at__isnull=True)
                pending_invitations.delete()
                new_membership = TeamMembership.objects.create(team=eligible_team, user=user, role=default_role)
                messages.success(self.request, _('Welcome to the team! You are now a part of {}.'.format(new_membership.team.name)))
                return super(InvitationConfirm, self).form_valid(form)
            else:
                organizer = eligible_team.teammembership_set.active().filter(role=TeamMembership.ORGANIZER).first()
                rejected_invitation = TeamInvitation.objects.create(
                    team=eligible_team,
                    organizer=organizer.user,
                    email=user.email,
                    role=default_role,
                    joined=invitation_confirmed,
                    responded_at=timezone.now()
                )
                return super(InvitationConfirm, self).form_valid(form)

        return super(InvitationConfirm, self).form_valid(form)


class StudyGroupFacilitatorSurvey(TemplateView):
    template_name = 'studygroups/facilitator_survey.html'

    def get_context_data(self, **kwargs):
        study_group = get_object_or_404(StudyGroup, uuid=kwargs.get('study_group_uuid'))
        context = super(StudyGroupFacilitatorSurvey, self).get_context_data(**kwargs)
        context['study_group'] = study_group
        context['survey_id'] = settings.TYPEFORM_FACILITATOR_SURVEY_FORM
        context['course'] = study_group.course.title
        context['goal'] = study_group.facilitator_goal
        context['goal_rating'] = study_group.facilitator_goal_rating
        meetings = study_group.meeting_set.active().order_by('meeting_date', 'meeting_time')
        attendance = [m.feedback_set.first().attendance if m.feedback_set.first() else None for m in meetings]
        if len(attendance) and attendance[0]:
            context['attendance_1'] = attendance[0]
        if len(attendance) > 1 and attendance[1]:
            context['attendance_2'] = attendance[1]
        if len(attendance) > 2 and attendance[-1]:
            context['attendance_n'] = attendance[-1]
        return context


@method_decorator(ensure_csrf_cookie, name='dispatch')
class FacilitatorDashboard(TemplateView):
    template_name = 'studygroups/facilitator_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(FacilitatorDashboard, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            email_validated = hasattr(user, 'profile') and user.profile.email_confirmed_at is not None

            if not email_validated:
                context["email_confirmation_url"] = reverse("email_confirm_request")

            context["first_name"] = user.first_name
            context["last_name"] = user.last_name
            context["city"] = user.profile.city
            context["bio"] = user.profile.bio
            context["avatar_url"] = f"{settings.PROTOCOL}://{settings.DOMAIN}" + user.profile.avatar.url if user.profile.avatar else None

            team_membership = TeamMembership.objects.active().filter(user=user).first()
            if team_membership:
                context['team_id'] = team_membership.team.id
                context['team_name'] = team_membership.team.name
                context['team_role'] = team_membership.role

                # add context for team organizers
                if team_membership.role == TeamMembership.ORGANIZER:
                    context['user_is_organizer'] = True
                    context['team_invitation_link'] = team_membership.team.team_invitation_link()
                    context['create_team_invitation_link'] = reverse('api_teams_create_invitation_url', args=(team_membership.team.id,))
                    context['delete_team_invitation_link'] = reverse('api_teams_delete_invitation_link', args=(team_membership.team.id,))
                    context['team_member_invitation_url'] = reverse('studygroups_team_member_invite', args=(team_membership.team.id,))
                    context['edit_team_url'] = reverse('studygroups_team_edit', args=(team_membership.team.id,))
                if team_membership.team.membership:
                    context['is_member_team'] = True
                if team_membership.team.membership or user.is_staff:
                    context['member_support_url'] = settings.MEMBER_SUPPORT_URL

        return context


@method_decorator(login_required, name='dispatch')
class LeaveTeam(DeleteView):
    model = TeamMembership
    success_url = reverse_lazy('account_settings')
    template_name = 'studygroups/confirm_leave_team.html'

    def get(self, request, *args, **kwargs):
        team_membership = self.get_object()
        if team_membership.role == TeamMembership.ORGANIZER:
            messages.warning(self.request, _('As the team organizer, you need to contact P2PU in order to leave the team.'))
            return http.HttpResponseRedirect(reverse('account_settings'))

        return super(LeaveTeam, self).get(request, *args, **kwargs)


@user_is_team_member
def weekly_update(request, team_id=None, year=None, month=None, day=None):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if month and day and year:
        today = today.replace(year=int(year), month=int(month), day=int(day))
    # get team for current user
    team = None
    if not request.user.is_staff:
        membership = TeamMembership.objects.active().filter(user=request.user).first()
        if membership:
            team = membership.team
    elif team_id:
        team = get_object_or_404(Team, pk=team_id)
    context = weekly_update_data(today, team)
    if request.user.is_staff:
        context['staff_update'] = True
    return render(request, 'studygroups/email/weekly-update.html', context)

