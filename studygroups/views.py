from datetime import datetime

from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives, send_mail
from django.contrib import messages
from django.conf import settings
from django import http
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView

from studygroups.models import Course, Location, StudyGroup, Application, Reminder, Feedback
from studygroups.models import StudyGroupMeeting
from studygroups.models import send_reminder
from studygroups.models import create_rsvp
from studygroups.forms import ApplicationForm, MessageForm, StudyGroupForm
from studygroups.forms import StudyGroupMeetingForm
from studygroups.forms import FeedbackForm
from studygroups.rsvp import check_rsvp_signature
from studygroups.decorators import user_is_group_facilitator


def landing(request):
    courses = Course.objects.all().order_by('key')

    for course in courses:
        course.studygroups = course.studygroup_set.all()

    context = {
        'courses': courses,
        'learning_circles': StudyGroup.objects.all(),
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
    user = request.GET['user']
    study_group = request.GET['study_group']
    meeting_date = request.GET['meeting_date']
    attending = request.GET['attending']
    sig = request.GET['sig']

    if (check_rsvp_signature(user, study_group, meeting_date, attending, sig)):
        rsvp = create_rsvp(user, int(study_group), meeting_date, attending)
        #TODO Show success message
    else:
        #TODO invalid RSVP link
        pass


@login_required
def facilitator(request):
    study_groups = StudyGroup.objects.filter(facilitator=request.user)
    study_groups = study_groups.filter(end_date__gt=timezone.now())
    context = {
        'study_groups': study_groups,
    }
    return render_to_response('studygroups/facilitator.html', context, context_instance=RequestContext(request))


@user_is_group_facilitator
def view_study_group(request, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    context = {
        'study_group': study_group,
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


class FeedbackCreate(CreateView):
    model = Feedback
    form_class = FeedbackForm
    success_url = reverse_lazy('studygroups_facilitator')

    def get_initial(self):
        meeting = get_object_or_404(StudyGroupMeeting, pk=self.kwargs.get('study_group_meeting_id'))
        return {
            'study_group_meeting': meeting,
        }


class ApplicationDelete(DeleteView):
    model = Application
    success_url = reverse_lazy('studygroups_facilitator')


@login_required
def organize(request):
    context = {
        'courses': Course.objects.all(),
        'study_groups': StudyGroup.objects.all(),
        'locations': Location.objects.all(),
        'facilitators': get_object_or_404(Group, name='facilitators').user_set.all()
    }
    return render_to_response('studygroups/organize.html', context, context_instance=RequestContext(request))


@login_required
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


@user_is_group_facilitator
def organize_messages(request, study_group_id):
    study_group = get_object_or_404(StudyGroup, pk=study_group_id)
    context = {
        'study_group': study_group,
    }
    return render_to_response('studygroups/organize_messages.html', context, context_instance=RequestContext(request))


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
        url = reverse('studygroups_organize_messages', args=(study_group_id,))
        messages.info(request, 'Message has already been sent and cannot be edited.')
        return http.HttpResponseRedirect(url)
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=reminder)
        if form.is_valid():
            reminder = form.save()
            messages.success(request, 'Message successfully edited')
            url = reverse('studygroups_organize_messages', args=(study_group_id,))
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
    to += [settings.DEFAULT_FROM_EMAIL]
    # Try to find a signup with the mobile number
    sender = '-'.join([sender[2:5], sender[5:8], sender[8:12]])
    signups = Application.objects.filter(mobile=sender)
    subject = 'New SMS reply from {0}'.format(sender)
    if signups.count() > 0:
        subject = 'New SMS reply from {0} <{1}>'.format(signups[0].name, sender)

    #TODO send to right facilitator
    send_mail(subject, message, settings.SERVER_EMAIL, to, fail_silently=False)
    return http.HttpResponse(status=200)
