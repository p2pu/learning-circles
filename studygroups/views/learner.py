import datetime
import dateutil.parser
import requests

from django.shortcuts import render, get_object_or_404
from studygroups.utils import render_to_string_ctx
from django.urls import reverse, reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.conf import settings
from django import http
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.text import slugify
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import Meeting
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import create_rsvp
from studygroups.models import application_mobile_opt_out
from studygroups.models import application_mobile_opt_out_revert
from studygroups.forms import ApplicationForm
from studygroups.forms import OptOutForm
from studygroups.forms import OptOutConfirmationForm
from studygroups.utils import check_rsvp_signature
from studygroups.utils import check_unsubscribe_signature
from studygroups.views.api import serialize_learning_circle

from surveys.models import LearnerSurveyResponse

import places

import string
import json
import urllib
import logging

logger = logging.getLogger(__name__)


def signup(request, location, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    if not study_group.deleted_at is None:
        raise http.Http404(_("Learning circle does not exist"))

    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        captcha_result = r.json()
        form = ApplicationForm(request.POST, initial={'study_group': study_group})
        if form.is_valid() and study_group.signup_open == True and study_group.draft == False and captcha_result.get('success'):
            application = form.save(commit=False)
            if application.email and Application.objects.active().filter(email__iexact=application.email, study_group=study_group).exists():
                old_application = Application.objects.active().filter(email__iexact=application.email, study_group=study_group).first()
                application.pk = old_application.pk
                application.created_at = old_application.created_at
                #TODO messages.success(request, 'Your signup details have been updated!')
            elif application.mobile and Application.objects.active().filter(mobile=application.mobile, study_group=study_group).exists():
                old_application = Application.objects.active().filter(mobile=application.mobile, study_group=study_group).first()
                application.pk = old_application.pk
                application.created_at = old_application.created_at
                #TODO messages.success(request, 'Your signup details have been updated!')

            # TODO - remove accepted_at or use accepting applications flow
            application.accepted_at = timezone.now()
            application.save()
            url = reverse('studygroups_signup_success', args=(study_group_id,) )
            return http.HttpResponseRedirect(url)
    else:
        form = ApplicationForm(initial={'study_group': study_group})

    meetings = study_group.meeting_set.active().order_by('meeting_date')
    last_meeting = meetings.last()

    context = {
        'form': form,
        'study_group': study_group,
        'meetings': meetings,
        'mapbox_token': settings.MAPBOX_TOKEN,
        'completed': last_meeting is not None and last_meeting.meeting_date < datetime.date.today(),
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY,
    }

    #if study_group.venue_address:
    #    context['map_url'] = "https://www.google.com/maps/search/?api=1&query={}".format(urllib.parse.quote(study_group.venue_address))

    return render(request, 'studygroups/signup.html', context)


def optout_confirm(request):
    # TODO this should have an option for both single opt out and multiple opt out
    if request.method == 'GET':
        user = request.GET.get('user')
        sig = request.GET.get('sig')
        form = OptOutConfirmationForm(initial={'user': user, 'sig': sig})
        return render(request, 'studygroups/optout_confirm.html', {'form': form})

    form = OptOutConfirmationForm(request.POST,
        initial={'user': request.GET.get('user'), 'sig': request.GET.get('sig')}
    )
    if form.is_valid():
        user = form.cleaned_data['user']
        sig = form.cleaned_data['sig']

        # Generator for conditions
        def conditions():
            yield user
            yield sig
            yield check_unsubscribe_signature(user, sig)
 
        if all(conditions()):
            signups = Application.objects.active().filter(pk=user)
            for signup in signups:
                signup.anonymize()
            signups.delete()
            messages.success(request, _('You successfully opted out of the learning circle.'))
            url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
        else:
            messages.error(request, _('Please check the email you received and make sure this is the correct URL.'))
        url = reverse('studygroups_facilitator')
        return http.HttpResponseRedirect(url)


class OptOutView(FormView):
    template_name = 'studygroups/optout.html'
    form_class = OptOutForm
    success_url = reverse_lazy('studygroups_facilitator')

    def form_valid(self, form):
        # Find all signups with email and send opt out confirmation
        form.send_optout_message()
        messages.info(self.request, _('You will shortly receive an email or text message confirming that you wish to opt out.'))
        return super(OptOutView, self).form_valid(form)


class SignupSuccess(TemplateView):
    template_name = 'studygroups/signup_success.html'

    def get_context_data(self, **kwargs):
        context = super(SignupSuccess, self).get_context_data(**kwargs)
        context['study_group'] = get_object_or_404(StudyGroup, pk=kwargs.get('study_group_id'))
        return context


def rsvp(request):
    user = request.GET.get('user')
    study_group = request.GET.get('study_group')
    attending = request.GET.get('attending')
    sig = request.GET.get('sig')
    meeting_date = None
    try:
        meeting_date = dateutil.parser.parse(request.GET.get('meeting_date'))
    except:
        # TODO log error
        pass

    # Generator for conditions
    def conditions():
        yield user
        yield study_group
        yield meeting_date
        yield attending
        yield sig
        yield meeting_date > timezone.now()
        yield check_rsvp_signature(user, study_group, meeting_date, attending, sig)

    if all(conditions()):
        rsvp = create_rsvp(user, int(study_group), meeting_date, attending)
        url = reverse('studygroups_rsvp_success')
        return http.HttpResponseRedirect(url)
    else:
        messages.error(request, 'Bad RSVP code')
        url = reverse('studygroups_facilitator')
        # TODO user http error code and display proper error page
        return http.HttpResponseRedirect(url)


@csrf_exempt
@require_http_methods(['POST'])
def receive_sms(request):
    # TODO - secure this callback
    sender = request.POST.get('From')
    message = request.POST.get('Body')

    STOP_LIST = ['STOP', 'STOPALL', 'UNSUBSCRIBE', 'CANCEL', 'END', 'QUIT']
    command = message.strip(string.punctuation + string.whitespace).upper()
    opt_out = command in STOP_LIST
    if opt_out:
        application_mobile_opt_out(sender)
        return http.HttpResponse(status=200)

    START_LIST = ['START', 'YES', 'UNSTOP']
    opt_in = command in START_LIST
    if opt_in:
        application_mobile_opt_out_revert(sender)
        return http.HttpResponse(status=200)

    to = []
    bcc = None
    subject = 'New SMS reply from {0}'.format(sender)
    context = {
        'message': message,
        'sender': sender,
    }

    # Only forward message to facilitator if there is a meeting in the future-ish
    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)
    meetings = Meeting.objects.active().filter(meeting_date__gte=yesterday)
    signups = Application.objects.active().filter(
        Q(mobile=sender) &
        Q(mobile_opt_out_at__isnull=True) &
        Q(study_group__in=meetings.values('study_group'))
    )

    # TODO handle user signed up to 2 learning circles
    if signups.count() == 1:
        signup = signups.first()
        context['signup'] = signup
        subject = _('New SMS reply from {0} <{1}>').format(signup.name, sender)
        to += [facilitator.user.email for facilitator in signup.study_group.facilitator_set.all()]
        next_meeting = signups.first().study_group.next_meeting()
        # TODO - replace this check with a check to see if the meeting reminder has been sent
        if next_meeting and next_meeting.meeting_datetime() - timezone.now() < datetime.timedelta(days=2):
            context['next_meeting'] = next_meeting
            context['rsvp_yes'] = next_meeting.rsvp_yes_link(sender)
            context['rsvp_no'] = next_meeting.rsvp_no_link(sender)

    text_body = render_to_string_ctx('studygroups/email/incoming_sms.txt', context)
    html_body = render_to_string_ctx('studygroups/email/incoming_sms.html', context)
    if len(to) == 0:
        to = [ a[1] for a in settings.ADMINS ]
    else:
        bcc = [ a[1] for a in settings.ADMINS ]

    notification = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to,
        bcc
    )
    notification.attach_alternative(html_body, 'text/html')
    notification.send()
    return http.HttpResponse(status=200)


@method_decorator(login_required, name="dispatch")
class StudyGroupParticipantView(TemplateView):
    template_name = 'studygroups/learning_circle_participant.html'

    def get(self, request, *args, **kwargs):
        study_group = get_object_or_404(StudyGroup, pk=kwargs.get('study_group_id'))
        application = Application.objects.active().filter(
            email__iexact=self.request.user.email,
            study_group=study_group
        ).first()

        # If a user isn't signed up or hasn't verified their email redirect them 
        # to the signup page
        if not application or not self.request.user.profile.email_confirmed_at:
            redirect_url = reverse(
                'studygroups_signup',
                args=(slugify(study_group.venue_name, allow_unicode=True), study_group.id)
            )
            return HttpResponseRedirect(redirect_url)

        context = self.get_context_data(**kwargs)
        context['study_group'] = study_group
        context['application'] = application
        meetings = study_group.meeting_set.active().order_by('meeting_date', 'meeting_time')
        messages = study_group.reminder_set.filter(sent_at__isnull=False)

        def _meeting_to_dict(meeting):
            d = meeting.to_dict()
            d['meeting_datetime'] = meeting.meeting_datetime()
            d['meeting_id'] = meeting.pk
            if meeting.rsvp_set.filter(application__email__iexact=self.request.user.email).exists():
                d['rsvp'] = meeting.rsvp_set.filter(application__email__iexact=self.request.user.email).first().attending
            return d

        def _message_to_dict(message):
            meeting = message.study_group_meeting
            d = {
                'sent_at': message.sent_at,
                'meeting': meeting.id if meeting else None, 
                'subject': message.email_subject,
                'body': message.email_body,
            }
            # Do we need meeting date + time also?
            # TODO should RSVP links be rewritten?
            return d

        signup_message_subject = render_to_string_ctx(
           'studygroups/email/learner_signup-subject.txt', {
                'application': application
            }
        ).strip('\n')

        signup_message_html = render_to_string_ctx(
            'studygroups/email/learner_signup.html', {
                'application': application,
                'facilitator_first_last_names': study_group.facilitators_display(),
                'email_in_browser': True,
            }
        )

        signup_message = {
            'subject': signup_message_subject,
            'body': signup_message_html,
            'sent_at': application.created_at,
        }

        survey_link = reverse(
            'studygroups_learner_survey',
            kwargs={'study_group_uuid': study_group.uuid}
        )

        survey_completed = LearnerSurveyResponse.objects.filter(learner=application, study_group=study_group).exists()

        react_data = {
            'learning_circle': serialize_learning_circle(study_group),
            'cu_credit': study_group.cu_credit,
            'meetings': list(map(_meeting_to_dict, meetings)),
            'messages': list(map(_message_to_dict, messages)),
            'survey_link': survey_link,
            'survey_completed': survey_completed,
            'signup_message': signup_message,
            'application_id': application.id, # TODO Is this used?
            'application': {
                'id': application.id,
                'name': application.name,
                'email': application.email,
            }
        }
        context['react_data'] = react_data

        return render(request, self.template_name, context)


class StudyGroupLearnerSurvey(TemplateView):
    template_name = 'studygroups/learner_survey.html'

    def get(self, request, *args, **kwargs):
        study_group = get_object_or_404(StudyGroup, uuid=kwargs.get('study_group_uuid'))

        if request.GET.get('learner', None):
            # if learner is in the query parameters,
            # store data in session and redirect to URL without query params
            # this is to minize the chance of a learner sharing 'their' survey URL
            learner_uuid = request.GET.get('learner', None)
            goal_met = request.GET.get('goal', None)
            try:
                application = study_group.application_set.get(uuid=learner_uuid)
                application.goal_met = goal_met
                application.save()
                request.session['learner_uuid'] = learner_uuid
            except ObjectDoesNotExist:
                pass

            redirect_url = reverse('studygroups_learner_survey', args=(study_group.uuid,))
            return HttpResponseRedirect(redirect_url)
        else:
            learner_uuid = request.session.get('learner_uuid', None)
            # TODO if the users refreshes the page, it will delete the session and log
            # the survey as anonymous
            # Move this to the survey done page
            if learner_uuid:
                del request.session['learner_uuid']
            try:
                application = study_group.application_set.get(uuid=learner_uuid)
                goal_met = application.goal_met
                context = {
                    'survey_id': settings.TYPEFORM_LEARNER_SURVEY_FORM,
                    'study_group_uuid': study_group.uuid,
                    'study_group_name': study_group.name,
                    'course_title': study_group.course.title,
                    'learner_uuid': application.uuid,
                    'facilitator_names': study_group.facilitators_display(),
                }
                if goal_met:
                    context['goal_met'] = goal_met
            except ObjectDoesNotExist:
                context = {
                    'survey_id': settings.TYPEFORM_LEARNER_SURVEY_FORM,
                    'study_group_uuid': study_group.uuid,
                    'study_group_name': study_group.name,
                    'course_title': study_group.course.title,
                    'facilitator_names': study_group.facilitators_display(),
                }

        return render(request, self.template_name, context)
