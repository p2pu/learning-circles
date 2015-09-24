import datetime
import dateutil

from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives, send_mail
from django.contrib import messages
from django.conf import settings
from django import http
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, TemplateView

from studygroups.models import Course, Location, StudyGroup, Application, Reminder, Feedback
from studygroups.models import StudyGroupMeeting
from studygroups.models import send_reminder
from studygroups.models import create_rsvp
from studygroups.models import report_data
from studygroups.forms import ApplicationForm, MessageForm, StudyGroupForm
from studygroups.forms import StudyGroupMeetingForm
from studygroups.forms import FeedbackForm
from studygroups.rsvp import check_rsvp_signature
from studygroups.decorators import user_is_group_facilitator
from studygroups.decorators import user_is_organizer


def landing(request):
    courses = Course.objects.all().order_by('key')

    for course in courses:
        course.studygroups = course.studygroup_set.all()

    context = {
        'courses': courses,
        'interest': {
            'courses': courses,
            'locations': Location.objects.all(),
        },
    }
    return render_to_response('studygroups/index.html', context, context_instance=RequestContext(request))


def signup(request, location, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            if application.contact_method == Application.EMAIL and Application.objects.filter(email=application.email, study_group=study_group):
                application = Application.objects.filter(email=application.email, study_group=study_group).first()
                #TODO messages.success(request, 'Your signup details have been updated!')
            elif application.contact_method == Application.TEXT and Application.objects.filter(mobile=application.mobile, study_group=study_group):
                application = Application.objects.filter(email=application.email, study_group=study_group).first()
                #TODO messages.success(request, 'Your signup details have been updated!')
            else:
                #TODO messages.success(request, 'You successfully signed up for a Learning Circle!')
                pass
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
def facilitator(request):
    study_groups = StudyGroup.objects.filter(facilitator=request.user)
    study_groups = study_groups.filter(end_date__gt=timezone.now())
    context = {
        'study_groups': study_groups,
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


class StudyGroupUpdate(UpdateView):
    model = StudyGroup
    fields = ['location_details', 'start_date', 'end_date', 'duration']
    success_url = reverse_lazy('studygroups_facilitator')
    pk_url_kwarg = 'study_group_id'


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
        to = [o.email for o in Group.objects.get(name='organizers').user_set.all()]
        # Try to find a signup with the mobile number
        context = {
            'feedback': form.cleaned_data,
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


@login_required
@user_is_organizer
def organize(request):
    context = {
        'courses': Course.objects.all(),
        'study_groups': StudyGroup.objects.all(),
        'meetings': StudyGroupMeeting.objects.all(),
        'locations': Location.objects.all(),
        'facilitators': get_object_or_404(Group, name='facilitators').user_set.all(),
        'today': timezone.now(),
    }
    return render_to_response('studygroups/organize.html', context, context_instance=RequestContext(request))


@login_required
@user_is_organizer
def report(request):
    study_groups = StudyGroup.objects.all()
    for study_group in study_groups:
        study_group.laptop_stats = {}
        study_group.laptop_stats['yes'] = study_group.application_set.all().filter(computer_access=Application.YES).count()
        study_group.laptop_stats['sometimes'] = study_group.application_set.all().filter(computer_access=Application.SOMETIMES).count()
        study_group.laptop_stats['no'] = study_group.application_set.all().filter(computer_access=Application.NO).count()
    context = {
        'study_groups': study_groups,
    }
    return render_to_response('studygroups/report.html', context, context_instance=RequestContext(request))


@login_required
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
    context.update(report_data(start_time, end_time))
    return render_to_response('studygroups/weekly-update.html', context, context_instance=RequestContext(request))


@user_is_group_facilitator
def email(request, study_group_id):
    # TODO - this piggy backs of Reminder, won't work of Reminder is coupled to StudyGroupMeeting
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            reminder = form.save()
            try:
                send_reminder(reminder)
                messages.success(request, 'Email successfully sent')
            except Exception as e:
                #TODO - catch specific error so that normal errors aren't masked by this
                messages.error(request, 'An error occured while sending group message.')

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
def messages_edit(request, study_group_id, message_id):
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
            if application.contact_method == Application.EMAIL and Application.objects.filter(email=application.email, study_group=study_group):
                application = Application.objects.filter(email=application.email, study_group=study_group).first()
                messages.success(request, 'Your signup details have been updated!')
            elif application.contact_method == Application.TEXT and Application.objects.filter(mobile=application.mobile, study_group=study_group):
                application = Application.objects.filter(email=application.email, study_group=study_group).first()
                messages.success(request, 'Your signup details have been updated!')
            else:
                messages.success(request, 'Successfully added member!')
            # TODO - remove accepted_at logic or use it. Currently just bypassing it.
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
    to = [ a[1] for a in settings.ADMINS ]
    # Try to find a signup with the mobile number
    sender = '-'.join([sender[2:5], sender[5:8], sender[8:12]])
    signups = Application.objects.filter(mobile=sender)
    subject = 'New SMS reply from {0}'.format(sender)
    if signups.count() > 0:
        # Send to all facilitators if user is signed up to more than 1 study group
        signup = next(s for s in signups)
        subject = 'New SMS reply from {0} <{1}>'.format(signup.name, sender)
        to += [ signup.study_group.facilitator.email for signup in signups]

    send_mail(subject, message, settings.SERVER_EMAIL, to, fail_silently=False)
    return http.HttpResponse(status=200)
