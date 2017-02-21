import datetime
import dateutil.parser

from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives, send_mail
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
from django.contrib.auth.models import User
from django.db.models import Count
from django.template.defaultfilters import slugify

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Application
from studygroups.models import Reminder
from studygroups.models import Feedback
from studygroups.models import StudyGroupMeeting
from studygroups.models import Team
from studygroups.models import TeamMembership
from studygroups.models import create_rsvp
from studygroups.models import get_team_users
from studygroups.forms import ApplicationForm
from studygroups.forms import OptOutForm
from studygroups.rsvp import check_rsvp_signature
from studygroups.utils import check_unsubscribe_signature

from uxhelpers.utils import json_response

import cities

def landing(request):
    two_weeks = (datetime.datetime.now() - datetime.timedelta(weeks=2)).date()

    study_group_ids = StudyGroupMeeting.objects.active().filter(meeting_date__gte=timezone.now()).values('study_group')
    study_groups = StudyGroup.objects.active().filter(id__in=study_group_ids, signup_open=True).order_by('start_date')

    city_list = study_groups.values('city').exclude(city='').annotate(total=Count('city')).order_by('-total')

    # NOTE: Not sure what the performance implication of the following line would be - it reads a file from disk every time
    #filter_func = lambda x: next( (c for c in cities.read_autocomplete_list() if c.lower().startswith(x['city'].lower())), (None) ) != None
    #city_list = filter(filter_func, city_list)

    context = {
        'learning_circles': study_groups[:50],
        'cities': city_list
    }
    return render_to_response('studygroups/index.html', context, context_instance=RequestContext(request))


class TeamPage(DetailView):
    model = Team
    template_name = 'studygroups/team_page.html'
    slug_field = 'page_slug'
    context_object_name = 'team'


    def get_context_data(self, **kwargs):
        context = super(TeamPage, self).get_context_data(**kwargs)
        two_weeks = (datetime.datetime.now() - datetime.timedelta(weeks=2)).date()

        team_users = TeamMembership.objects.filter(team=self.object).values('user')
        study_group_ids = StudyGroupMeeting.objects.active()\
                .filter(meeting_date__gte=timezone.now())\
                .values('study_group')
        study_groups = StudyGroup.objects.active()\
                .filter(facilitator__in=team_users)\
                .filter(id__in=study_group_ids, signup_open=True)\
                .order_by('start_date')

        context['learning_circles'] = study_groups
        return context


class CourseListView(ListView):
    def get_queryset(self):
        return Course.objects.filter(created_by__isnull=True)


def city(request, city_name):
    matches = [ c for c in cities.read_autocomplete_list() if c.lower().startswith(city_name.lower()) ]

    if len(matches) == 1 and matches[0] != city_name:
        return http.HttpResponseRedirect(reverse('studygroups_city', args=(matches[0],)))

    #TODO handle multiple matches. Ex. city_name = Springfield
    #two_weeks = (datetime.datetime.now() - datetime.timedelta(weeks=2)).date()
    #learning_circles = StudyGroup.objects.active().filter(city__istartswith=city_name)

    study_group_ids = StudyGroupMeeting.objects.active().filter(meeting_date__gte=timezone.now()).values('study_group')
    study_group_ids = study_group_ids.filter(study_group__city__istartswith=city_name)
    learning_circles = StudyGroup.objects.active().filter(id__in=study_group_ids, signup_open=True).order_by('start_date')

    #learning_circles = learning_circles.filter(signup_open=True, start_date__gte=two_weeks).order_by('start_date')

    context = {
        'learning_circles': learning_circles,
        'city': city_name
    }
    return render_to_response('studygroups/city_list.html', context, context_instance=RequestContext(request))


def studygroups(request):
    #TODO only accept GET requests 
    study_groups = StudyGroup.objects.active()
    if 'course_id' in request.GET:
        study_groups = study_groups.filter(course_id=request.GET.get('course_id'))
    
    def to_json(sg):
        data = {
            "course_title": sg.course.title,
            "facilitator": sg.facilitator.first_name + " " + sg.facilitator.last_name,
            "venue": sg.venue_name,
            "venue_address": sg.venue_address + ", " + sg.city,
            "day": sg.day(),
            "start_date": sg.start_date,
            "meeting_time": sg.meeting_time,
            "time_zone": sg.timezone_display(),
            "end_time": sg.end_time(),
            "weeks": sg.studygroupmeeting_set.active().count(),
            "url": "https://learningcircles.p2pu.org" + reverse('studygroups_signup', args=(slugify(sg.venue_name), sg.id,)),
        }
        if sg.image:
            data["image_url"] = "https://learningcircles.p2pu.org" + sg.image.url
        #TODO else set default image URL
        return data

    data = [ to_json(sg) for sg in study_groups ]
    return json_response(request, data)


def signup(request, location, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    if not study_group.deleted_at is None:
        return http.HttpResponseGone()

    if request.method == 'POST':
        form = ApplicationForm(request.POST, initial={'study_group': study_group})
        if form.is_valid() and study_group.signup_open is True:
            application = form.save(commit=False)
            if application.email and Application.objects.active().filter(email=application.email, study_group=study_group).exists():
                old_application = Application.objects.active().filter(email=application.email, study_group=study_group).first()
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
            notification_subject = render_to_string(
                    'studygroups/notifications/application-subject.txt',
                    {'application': application}
            ).strip('\n')
            notification_body = render_to_string(
                'studygroups/notifications/application.txt', 
                {'application': application}
            )
            notification_html = render_to_string(
                'studygroups/notifications/application.html', 
                {'application': application}
            )
            to = [study_group.facilitator.email]
            notification = EmailMultiAlternatives(
                notification_subject,
                notification_body,
                settings.SERVER_EMAIL,
                to
            )
            notification.attach_alternative(notification_html, 'text/html')
            notification.send()

            url = reverse('studygroups_signup_success', args=(study_group_id,) )
            return http.HttpResponseRedirect(url)
    else:
        form = ApplicationForm(initial={'study_group': study_group})

    context = {
        'form': form,
        'study_group': study_group,
    }
    return render_to_response('studygroups/signup.html', context, context_instance=RequestContext(request))


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
        messages.success(request, _('You successfully opted out of the Learning Circle.'))
    else:
        messages.error(request, _('Please check the email you received and make sure this is the correct URL.'))

    url = reverse('studygroups_landing')
    return http.HttpResponseRedirect(url)


class OptOutView(FormView):
    template_name = 'studygroups/optout.html'
    form_class = OptOutForm
    success_url = reverse_lazy('studygroups_landing')

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
        url = reverse('studygroups_landing')
        # TODO user http error code and display proper error page
        return http.HttpResponseRedirect(url)


@csrf_exempt
@require_http_methods(['POST'])
def receive_sms(request):
    # TODO - secure this callback
    sender = request.POST.get('From')
    message = request.POST.get('Body')
    to = []
    bcc = None
    # Try to find a signup with the mobile number
    #sender = '-'.join([sender[2:5], sender[5:8], sender[8:12]])
    subject = 'New SMS reply from {0}'.format(sender)
    context = {
        'message': message,
        'sender': sender,
    }
    signups = Application.objects.active().filter(mobile=sender)
    if signups.count() > 0:
        # Send to all facilitators if user is signed up to more than 1 study group
        signup = next(s for s in signups)
        context['signup'] = signup
        subject = 'New SMS reply from {0} <{1}>'.format(signup.name, sender)
        to += [ signup.study_group.facilitator.email for signup in signups]

    if len(to) == 0:
        to = [ a[1] for a in settings.ADMINS ]
    else:
        bcc = [ a[1] for a in settings.ADMINS ]
    
    if signups.count() == 1 and signups.first().study_group.next_meeting():
        next_meeting = signups.first().study_group.next_meeting()
        # TODO - replace this check with a check to see if the meeting reminder has been sent
        if next_meeting.meeting_datetime() - timezone.now() < datetime.timedelta(days=2):
            context['next_meeting'] = next_meeting
            context['rsvp_yes'] = next_meeting.rsvp_yes_link(sender)
            context['rsvp_no'] = next_meeting.rsvp_no_link(sender)

    text_body = render_to_string('studygroups/incoming_sms.txt', context)
    html_body = render_to_string('studygroups/incoming_sms.html', context)
    notification = EmailMultiAlternatives(
        subject,
        text_body,
        settings.SERVER_EMAIL,
        to,
        bcc
    )
    notification.attach_alternative(html_body, 'text/html')
    notification.send()
    return http.HttpResponse(status=200)
