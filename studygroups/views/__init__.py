import datetime
import dateutil

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
from django.views.generic.base import View, RedirectView
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, TemplateView
from django.contrib.auth.models import User
from django.forms import modelform_factory
from django.db.models import Count
from django.template.defaultfilters import slugify

from studygroups.models import Course, StudyGroup, Application, Reminder, Feedback
from studygroups.models import Organizer, Facilitator, TeamMembership
from studygroups.models import StudyGroupMeeting
from studygroups.models import send_reminder
from studygroups.models import create_rsvp
from studygroups.models import report_data
from studygroups.models import generate_all_meetings
from studygroups.models import get_team_users
from studygroups.models import get_study_group_organizers
from studygroups.forms import ApplicationForm, MessageForm, StudyGroupForm
from studygroups.forms import StudyGroupMeetingForm
from studygroups.forms import FeedbackForm
from studygroups.forms import OptOutForm
from studygroups.rsvp import check_rsvp_signature
from studygroups.decorators import user_is_group_facilitator
from studygroups.decorators import user_is_organizer
from studygroups.utils import check_unsubscribe_signature

from facilitate import FacilitatorCreate, FacilitatorUpdate, FacilitatorDelete
from facilitate import FacilitatorSignup
from facilitate import FacilitatorSignupSuccess
from facilitate import FacilitatorStudyGroupCreate

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

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
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
            #TODO - get group to bcc from django user group
            bcc = [ a[1] for a in settings.ADMINS ]
            notification = EmailMultiAlternatives(
                notification_subject,
                notification_body,
                settings.SERVER_EMAIL,
                to,
                bcc
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
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    context = {
        'study_group': study_group,
        'today': timezone.now()
    }
    return render_to_response('studygroups/view_study_group.html', context, context_instance=RequestContext(request))


class MeetingCreate(CreateView):
    model = StudyGroupMeeting
    form_class = StudyGroupMeetingForm
    success_url = reverse_lazy('studygroups_facilitator')

    def get_initial(self):
        study_group = get_object_or_404(StudyGroup, pk=self.kwargs.get('study_group_id'))
        return {
            'study_group': study_group,
        }


class MeetingUpdate(UpdateView):
    model = StudyGroupMeeting
    form_class = StudyGroupMeetingForm
    success_url = reverse_lazy('studygroups_facilitator')


class MeetingDelete(DeleteView):
    model = StudyGroupMeeting
    success_url = reverse_lazy('studygroups_facilitator')


class FeedbackDetail(DetailView):
    model = Feedback


class FeedbackCreate(CreateView):
    model = Feedback
    form_class = FeedbackForm
    success_url = reverse_lazy('studygroups_facilitator')

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


class ApplicationDelete(DeleteView):
    model = Application
    success_url = reverse_lazy('studygroups_facilitator')
    template_name = 'studygroups/confirm_delete.html'


@user_is_organizer
def organize(request):
    # TODO 
    # - Only show learning circles with meetings in the future
    # - Only show meetings for current week 
    today = datetime.datetime.now().date()
    two_weeks_ago = today - datetime.timedelta(weeks=2, days=today.weekday())
    two_weeks = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(weeks=3)
    study_groups = StudyGroup.objects.active()
    facilitators = Facilitator.objects.all()    

    if not request.user.is_staff:
        team_users = get_team_users(request.user)
        study_groups = study_groups.filter(facilitator__in=team_users)
        facilitators = facilitators.filter(user__in=team_users)

    context = {
        'courses': Course.objects.all(),
        'study_groups': study_groups,
        'meetings': StudyGroupMeeting.objects.active().filter(study_group__in=StudyGroup.objects.active(), meeting_date__gte=two_weeks_ago).exclude(meeting_date__gte=two_weeks),
        'facilitators': facilitators,
        'today': timezone.now(),
    }
    return render_to_response('studygroups/organize.html', context, context_instance=RequestContext(request))


class CourseCreate(CreateView):
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
        # TODO - courses created by organizers will always be global
        if Organizer.objects.filter(user=self.request.user).exists():
            return super(CourseCreate, self).form_valid(form)
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return http.HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if Facilitator.objects.filter(user=self.request.user).exists():
            return reverse('studygroups_facilitator_studygroup_create')
        return reverse_lazy('studygroups_organize')


class CourseUpdate(UpdateView):
    model = Course
    fields = [    
        'title',
        'provider',
        'link',
        'start_date',
        'duration',
        'prerequisite',
        'time_required',
        'caption',
    ]
    success_url = reverse_lazy('studygroups_organize')


class CourseDelete(DeleteView):
    model = Course
    success_url = reverse_lazy('studygroups_organize')
    template_name = 'studygroups/confirm_delete.html'


class StudyGroupCreate(CreateView):
    model = StudyGroup
    form_class = StudyGroupForm
    success_url = reverse_lazy('studygroups_organize')

    def form_valid(self, form):
        self.object = form.save()
        generate_all_meetings(self.object)
        return http.HttpResponseRedirect(self.get_success_url())


## This form is used by facilitators
class StudyGroupUpdate(UpdateView):
    model = StudyGroup
    form_class =  modelform_factory(StudyGroup, StudyGroupForm, exclude=['facilitator'])
    success_url = reverse_lazy('studygroups_facilitator')
    pk_url_kwarg = 'study_group_id'


class StudyGroupDelete(DeleteView):
    model = StudyGroup
    template_name = 'studygroups/confirm_delete.html'
    pk_url_kwarg = 'study_group_id'

    def get_success_url(self):
        if Facilitator.objects.filter(user=self.request.user).exists():
            return reverse_lazy('studygroups_facilitator')
        return reverse_lazy('studygroups_organize')


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
        if Facilitator.objects.filter(user=self.request.user).exists():
            return reverse_lazy('studygroups_facilitator')
        return reverse_lazy('studygroups_organize')


@user_is_organizer
def report(request):
    study_groups = StudyGroup.objects.active()
    for study_group in study_groups:
        study_group.laptop_stats = {}
        #TODO study_group.laptop_stats['yes'] = study_group.application_set.all().filter(computer_access=Application.YES).count()
        #TODO study_group.laptop_stats['sometimes'] = study_group.application_set.all().filter(computer_access=Application.SOMETIMES).count()
        #TODO study_group.laptop_stats['no'] = study_group.application_set.all().filter(computer_access=Application.NO).count()
    context = {
        'study_groups': study_groups,
    }
    return render_to_response('studygroups/report.html', context, context_instance=RequestContext(request))


@user_is_organizer
def weekly_report(request, year=None, month=None, day=None ):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if month and day and year:
        today = today.replace(year=int(year), month=int(month), day=int(day))
    start_time = today - datetime.timedelta(days=today.weekday())
    end_time = start_time + datetime.timedelta(days=7)
    context = {
        'start_time': start_time,
        'end_time': end_time,
    }
    # get team for current user
    team = None
    membership = TeamMembership.objects.filter(user=request.user, role=TeamMembership.ORGANIZER).first()
    if membership:
        team = membership.team

    context.update(report_data(start_time, end_time, team))
    return render_to_response('studygroups/weekly-update.html', context, context_instance=RequestContext(request))


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
        form = ApplicationForm(request.POST)
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

            url = reverse('studygroups_facilitator')
            return http.HttpResponseRedirect(url)
    else:
        form = ApplicationForm(initial={'study_group': study_group})

    context = {
        'form': form,
        'study_group': study_group,
    }
    return render_to_response('studygroups/add_member.html', context, context_instance=RequestContext(request))


@csrf_exempt
@require_http_methods(['POST'])
def receive_sms(request):
    # TODO - secure this callback
    sender = request.POST.get('From')
    message = request.POST.get('Body')
    to = []
    bcc = None
    # Try to find a signup with the mobile number
    sender = '-'.join([sender[2:5], sender[5:8], sender[8:12]])
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
