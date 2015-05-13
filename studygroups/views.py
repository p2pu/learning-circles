from datetime import datetime

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django import http
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from studygroups.models import Course, StudyGroup, Application, Reminder
from studygroups.models import send_reminder
from studygroups.forms import ApplicationForm, EmailForm
from studygroups.sms import send_message


def landing(request):
    courses = Course.objects.all().order_by('key')

    for course in courses:
        course.studygroups = course.studygroup_set.all()

    context = {
        'courses': courses,
    }
    return render_to_response('studygroups/index.html', context, context_instance=RequestContext(request))


def apply(request):
    group = request.GET.get('group', None)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            messages.success(request, 'You successfully applied to join a study group!')
            notification_body = render_to_string(
                'studygroups/notifications/application.txt', 
                {'application': application}
            )
            #TODO - get group to send to from django user group
            to = [ a[1] for a in settings.ADMINS ]
            send_mail('New study group application', notification_body, settings.SERVER_EMAIL, to, fail_silently=False)
            url = reverse('studygroups_landing')
            return http.HttpResponseRedirect(url)
    else:
        form = ApplicationForm(initial={'study_group': group})

    context = {
        'form': form
    }
    return render_to_response('studygroups/apply.html', context, context_instance=RequestContext(request))


@login_required
def organize(request):
    context = {
        'courses': Course.objects.all(),
        'study_groups': StudyGroup.objects.all(),
    }
    return render_to_response('studygroups/organize.html', context, context_instance=RequestContext(request))


def organize_messages(request, study_group_id):
    study_group = StudyGroup.objects.get(id=study_group_id)
    context = {
        'study_group': study_group,
    }
    return render_to_response('studygroups/organize_messages.html', context, context_instance=RequestContext(request))
   


@login_required
def email(request, study_group_id):
    study_group = StudyGroup.objects.get(id=study_group_id)
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            reminder = Reminder()
            reminder.study_group = study_group
            reminder.email_subject = form.cleaned_data['subject']
            reminder.email_body = form.cleaned_data['body']
            reminder.sms_body = form.cleaned_data['sms_body']
            reminder.save()
            try:
                send_reminder(reminder)
                messages.success(request, 'Email successfully sent')
            except Exception as e:
                messages.error(request, 'An error occured while sending group message.')

            url = reverse('studygroups_organize')
            return http.HttpResponseRedirect(url)
    else:
        form = EmailForm(initial={'study_group_id': study_group.id})

    context = {
        'study_group': study_group,
        'course': study_group.course,
        'form': form
    }
    return render_to_response('studygroups/email.html', context, context_instance=RequestContext(request))


@csrf_exempt
@require_http_methods(['POST'])
def receive_sms(request):
    # TODO - secure this callback
    sender = request.POST.get('From')
    message = request.POST.get('Body')
    to = [ a[1] for a in settings.ADMINS ]
    to += [settings.DEFAULT_FROM_EMAIL]
    send_mail('New SMS reply from {0}'.format(sender), message, settings.SERVER_EMAIL, to, fail_silently=False)
    return http.HttpResponse(status=200)
