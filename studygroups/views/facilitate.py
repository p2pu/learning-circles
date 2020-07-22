from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django import http
from django import forms
from django.forms import modelform_factory, HiddenInput
from studygroups.utils import render_to_string_ctx
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

import json
import datetime
import requests
import logging

from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Course
from studygroups.models import Application
from studygroups.models import Feedback
from studygroups.models import Reminder
from studygroups.forms import CourseForm
from studygroups.forms import StudyGroupForm
from studygroups.forms import MeetingForm
from studygroups.forms import FeedbackForm
from studygroups.tasks import send_reminder
from studygroups.tasks import send_meeting_change_notification
from studygroups.models import generate_all_meetings
from studygroups.models import get_study_group_organizers
from studygroups.decorators import user_is_group_facilitator
from studygroups.decorators import study_group_is_published
from studygroups.charts import OverallRatingBarChart
from studygroups.discourse import create_discourse_topic
from studygroups.views.api import _course_to_json
from studygroups.models.team import eligible_team_by_email_domain

logger = logging.getLogger(__name__)

@login_required
def login_redirect(request):
    url = reverse('studygroups_facilitator')
    return http.HttpResponseRedirect(url)


@login_required
def facilitator(request):
    today = datetime.datetime.now().date()
    two_weeks_ago = today - datetime.timedelta(weeks=2, days=today.weekday())

    study_groups = StudyGroup.objects.active().filter(facilitator=request.user)
    current_study_groups = study_groups.filter(
        Q(id__in=Meeting.objects.active().filter(meeting_date__gte=two_weeks_ago).values('study_group')) |
        Q(draft=True, end_date__gte=two_weeks_ago)
    )
    past_study_groups = study_groups.exclude(id__in=current_study_groups)
    team = None
    if TeamMembership.objects.active().filter(user=request.user).exists():
        team = TeamMembership.objects.active().filter(user=request.user).first().team
    invitation = TeamInvitation.objects.filter(email__iexact=request.user.email, responded_at__isnull=True).first()
    context = {
        'current_study_groups': current_study_groups,
        'past_study_groups': past_study_groups,
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
    user_is_facilitator = study_group.facilitator == request.user
    facilitator_is_organizer = TeamMembership.objects.active().filter(user=request.user, role=TeamMembership.ORGANIZER).exists()
    dashboard_url = reverse('studygroups_facilitator')

    if facilitator_is_organizer and not user_is_facilitator:
        dashboard_url = reverse('studygroups_organize')

    context = {
        'study_group': study_group,
        'today': timezone.now(),
        'dashboard_url': dashboard_url
    }
    return render(request, 'studygroups/view_study_group.html', context)


class FacilitatorRedirectMixin(object):
    """ Redirect to the study group page """

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('studygroups_view_study_group', args=(self.kwargs.get('study_group_id'),))


@method_decorator(user_is_group_facilitator, name="dispatch")
@method_decorator(study_group_is_published, name='dispatch')
class MeetingCreate(FacilitatorRedirectMixin, CreateView):
    model = Meeting
    form_class = MeetingForm

    def get_initial(self):
        study_group_id = self.kwargs.get('study_group_id')
        study_group = get_object_or_404(StudyGroup, pk=study_group_id)
        return {
            'study_group': study_group,
        }


@method_decorator(user_is_group_facilitator, name="dispatch")
@method_decorator(study_group_is_published, name='dispatch')
class MeetingUpdate(FacilitatorRedirectMixin, UpdateView):
    model = Meeting
    form_class = MeetingForm

    def form_valid(self, form):
        # check if update meeting has an unsent reminder associated?
        # self.object contains updated values, but not yet saved
        # self.object have been updated by the form :(
        if self.object.reminder_set.count() == 1:
            reminder = self.object.reminder_set.first()
            if not reminder.sent_at:
                # The reminder will be generated again if the meeting is still in the future
                # This should only happen between 2 days and 4 days before the original start date.
                reminder.delete()
            else:
                # a reminder was sent already
                # orphan reminder if the meeting is now in the future.
                if self.object.meeting_datetime() > timezone.now():
                    reminder.study_group_meeting = None
                    reminder.save()

                # if meeting was scheduled for a date in the future
                # let learners know the details have changed
                original_meeting = Meeting.objects.get(pk=self.object.pk)
                if original_meeting.meeting_datetime() > timezone.now():
                    send_meeting_change_notification.delay(original_meeting, self.object)

        return super().form_valid(form)


@method_decorator(user_is_group_facilitator, name="dispatch")
@method_decorator(study_group_is_published, name='dispatch')
class MeetingDelete(FacilitatorRedirectMixin, DeleteView):
    model = Meeting


@method_decorator(user_is_group_facilitator, name="dispatch")
class FeedbackDetail(FacilitatorRedirectMixin, DetailView):
    model = Feedback


@method_decorator(user_is_group_facilitator, name="dispatch")
@method_decorator(study_group_is_published, name='dispatch')
class FeedbackCreate(FacilitatorRedirectMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm

    def get_initial(self):
        meeting = get_object_or_404(Meeting, pk=self.kwargs.get('study_group_meeting_id'))
        return {
            'study_group_meeting': meeting,
        }

    def form_valid(self, form):
        # send notification to organizers about feedback
        to = [] #TODO should we send this to someone if the facilitators is not part of a team? - for now, don't worry, this notification is likely to be removed.
        meeting = get_object_or_404(Meeting, pk=self.kwargs.get('study_group_meeting_id'))
        organizers = get_study_group_organizers(meeting.study_group)
        if organizers:
            to = [o.email for o in organizers]

        context = {
            'feedback': form.save(commit=False),
            'study_group_meeting': self.get_initial()['study_group_meeting']
        }
        subject = render_to_string_ctx('studygroups/email/feedback-submitted-subject.txt', context).strip('\n')
        html_body = render_to_string_ctx('studygroups/email/feedback-submitted.html', context)
        text_body = render_to_string_ctx('studygroups/email/feedback-submitted.txt', context)
        notification = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, to)
        notification.attach_alternative(html_body, 'text/html')
        notification.send()
        return super(FeedbackCreate, self).form_valid(form)


@method_decorator(user_is_group_facilitator, name="dispatch")
class FeedbackUpdate(FacilitatorRedirectMixin, UpdateView):
    model = Feedback
    form_class = FeedbackForm


@method_decorator(user_is_group_facilitator, name="dispatch")
class ApplicationUpdate(FacilitatorRedirectMixin, UpdateView):
    model = Application
    form_class =  modelform_factory(Application, fields=['study_group', 'name', 'email', 'mobile'], widgets={'study_group': HiddenInput})
    template_name = 'studygroups/add_member.html'


@method_decorator(user_is_group_facilitator, name="dispatch")
class ApplicationDelete(FacilitatorRedirectMixin, DeleteView):
    model = Application
    success_url = reverse_lazy('studygroups_facilitator')
    template_name = 'studygroups/confirm_delete.html'


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
        similar_courses = [ _course_to_json(course) for course in self.object.similar_courses()]

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
        other_study_groups =  StudyGroup.objects.active().filter(course=course).exclude(facilitator=request.user)
        study_groups = StudyGroup.objects.active().filter(course=course, facilitator=request.user)
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
        context['hide_footer'] = True
        context['tinymce_api_key'] = settings.TINYMCE_API_KEY
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

        #generate_all_meetings(study_group)
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
        context['hide_footer'] = True
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
            self.object.meeting_set.delete()
            generate_all_meetings(self.object)
        return return_value


@method_decorator(user_is_group_facilitator, name="dispatch")
class StudyGroupDelete(FacilitatorRedirectMixin, DeleteView):
    # TODO Need to fix back link for confirmation page
    model = StudyGroup
    template_name = 'studygroups/confirm_delete.html'
    pk_url_kwarg = 'study_group_id'


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
        profile = study_group.facilitator.profile
        if profile.email_confirmed_at is None:
            messages.warning(self.request, _("You need to confirm your email address before you can publish a learning circle."));
        else:
            messages.success(self.request, _("Your learning circle has been published."));
            study_group.draft = False
            study_group.save()
            generate_all_meetings(study_group)

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
    # TODO - this piggy backs of Reminder, won't work of Reminder is coupled to Meeting
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
@study_group_is_published
def message_edit(request, study_group_id, message_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    reminder = get_object_or_404(Reminder, pk=message_id)
    url = reverse('studygroups_view_study_group', args=(study_group_id,))
    if not reminder.sent_at == None:
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
@study_group_is_published
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
            return http.HttpResponseRedirect(url)
    else:
        form = form_class(initial={'study_group': study_group})

    context = {
        'form': form,
        'study_group': study_group,
    }
    return render(request, 'studygroups/add_member.html', context)


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
        context = super(InvitationConfirm, self).get_context_data(**kwargs)
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
        study_group.facilitator_goal_rating = self.request.GET.get('goal_rating', None)
        study_group.save()

        context = super(StudyGroupFacilitatorSurvey, self).get_context_data(**kwargs)
        context['survey_id'] = settings.TYPEFORM_FACILITATOR_SURVEY_FORM
        context['study_group_uuid'] = study_group.uuid
        context['study_group_name'] = study_group.name
        context['course'] = study_group.course.title
        context['goal'] = study_group.facilitator_goal
        context['goal_rating'] = self.request.GET.get('goal_rating', '')
        meetings = study_group.meeting_set.active().order_by('meeting_date', 'meeting_time')
        attendance = [m.feedback_set.first().attendance if m.feedback_set.first() else None for m in meetings]
        if len(attendance) and attendance[0]:
            context['attendance_1'] = attendance[0]
        if len(attendance) > 1 and attendance[1]:
            context['attendance_2'] = attendance[1]
        if len(attendance) > 2 and attendance[-1]:
            context['attendance_n'] = attendance[-1]

        # TODO context['no_studygroup'] = self.request.GET.get('nostudygroup', False)
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
                    context['team_invitation_url'] = team_membership.team.team_invitation_url()
                    context['create_team_invitation_url'] = reverse('api_teams_create_invitation_url', args=(team_membership.team.id,))
                    context['delete_team_invitation_url'] = reverse('api_teams_delete_invitation_url', args=(team_membership.team.id,))
                    context['team_member_invitation_url'] = reverse('studygroups_team_member_invite', args=(team_membership.team.id,))
                    context['edit_team_url'] = reverse('studygroups_team_edit', args=(team_membership.team.id,))

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

