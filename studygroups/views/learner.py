import datetime
import dateutil.parser

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
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist

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
from studygroups.utils import check_rsvp_signature
from studygroups.utils import check_unsubscribe_signature

import string
import cities
import json


class TeamPage(DetailView):
    model = Team
    template_name = 'studygroups/team_page.html'
    slug_field = 'page_slug'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super(TeamPage, self).get_context_data(**kwargs)
        two_weeks = (datetime.datetime.now() - datetime.timedelta(weeks=2)).date()

        team_users = TeamMembership.objects.active().filter(team=self.object).values('user')
        study_group_ids = Meeting.objects.active()\
                .filter(meeting_date__gte=timezone.now())\
                .values('study_group')
        study_groups = StudyGroup.objects.published()\
                .filter(facilitator__in=team_users)\
                .filter(id__in=study_group_ids, signup_open=True)\
                .order_by('start_date')

        context['learning_circles'] = study_groups
        return context


def city(request, city_name):
    matches = [ c for c in cities.read_autocomplete_list() if c.lower().startswith(city_name.lower()) ]

    if len(matches) == 1 and matches[0] != city_name:
        return http.HttpResponseRedirect(reverse('studygroups_city', args=(matches[0],)))

    #TODO handle multiple matches. Ex. city_name = Springfield
    #two_weeks = (datetime.datetime.now() - datetime.timedelta(weeks=2)).date()
    #learning_circles = StudyGroup.objects.published().filter(city__istartswith=city_name)

    study_group_ids = Meeting.objects.active().filter(meeting_date__gte=timezone.now()).values('study_group')
    study_group_ids = study_group_ids.filter(study_group__city__istartswith=city_name)
    learning_circles = StudyGroup.objects.published().filter(id__in=study_group_ids, signup_open=True).order_by('start_date')

    #learning_circles = learning_circles.filter(signup_open=True, start_date__gte=two_weeks).order_by('start_date')

    context = {
        'learning_circles': learning_circles,
        'city': city_name
    }
    return render(request, 'studygroups/city_list.html', context)


def signup(request, location, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    if not study_group.deleted_at is None:
        return http.HttpResponseGone() ## TODO


    if request.method == 'POST':
        form = ApplicationForm(request.POST, initial={'study_group': study_group})
        if form.is_valid() and study_group.signup_open == True and study_group.draft == False:
            application = form.save(commit=False)
            if application.email and Application.objects.active().filter(email__iexact=application.email, study_group=study_group).exists():
                old_application = Application.objects.active().filter(email__iexact=application.email, study_group=study_group).first()
                application.pk = old_application.pk
                application.created_at = old_application.created_at
                #TODO messages.success(request, 'Your signup details have been updated!')

            if application.mobile and Application.objects.active().filter(mobile=application.mobile, study_group=study_group).exists():
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

    context = {
        'form': form,
        'study_group': study_group,
    }
    return render(request, 'studygroups/signup.html', context)


def optout_confirm(request):
    user = request.GET.get('user')
    sig = request.GET.get('sig')

    # Generator for conditions
    def conditions():
        yield user
        yield sig
        yield check_unsubscribe_signature(user, sig)

    if all(conditions()):
        signup = Application.objects.active().filter(pk=user)
        signup.delete()
        messages.success(request, _('You successfully opted out of the learning circle.'))
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
        # TODO i18n
        subject = 'New SMS reply from {0} <{1}>'.format(signup.name, sender)
        to += [ signup.study_group.facilitator.email ]
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
                request.session['goal_met'] = goal_met

                redirect_url = reverse('studygroups_learner_survey', kwargs={'study_group_uuid': kwargs.get('study_group_uuid')})
                return HttpResponseRedirect(redirect_url)
            except ObjectDoesNotExist:
                redirect_url = reverse('studygroups_learner_survey', kwargs={'study_group_uuid': kwargs.get('study_group_uuid')})
                return HttpResponseRedirect(redirect_url)
        else:
            learner_uuid = request.session.get('learner_uuid', None)
            goal_met = request.session.get('goal_met', None)
            # TODO consider unsetting session variable here
            try:
                application = study_group.application_set.get(uuid=learner_uuid)
                signup_questions = json.loads(application.signup_questions)
                learner_goal = signup_questions.get('goals', None)
                contact = application.email if application.email else application.mobile

                context = {
                    'study_group_uuid': study_group.uuid,
                    'course_title': study_group.course.title,
                    'contact': contact,
                    'goal': learner_goal,
                    'goal_met': goal_met,
                    'learner_name': application.name,
                    'facilitator_name': study_group.facilitator.first_name,
                    'survey_id': settings.TYPEFORM_LEARNER_SURVEY_FORM,
                }
            except ObjectDoesNotExist:
                context = {
                    'study_group_uuid': study_group.uuid,
                    'course_title': study_group.course.title,
                    'facilitator_name': study_group.facilitator.first_name,
                    'survey_id': settings.TYPEFORM_LEARNER_SURVEY_FORM,
                }

        # TODO if the users refreshes the page, it will delete the session and log the survey as anonymous
        request.session.clear()  #TODO this logs anyone out of learningcircles.p2pu.org when they visit this URL
        return render(request, self.template_name, context)
