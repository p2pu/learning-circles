from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django import http

import twilio
import twilio.rest

from studygroups.models import Course, StudyGroup, StudyGroupSignup
from studygroups.forms import SignupForm, EmailForm

def landing(request):
    context = {
        'courses': Course.objects.all(),
        'study_groups': Course.objects.all(),
    }
    return render_to_response('studygroups/index.html', context, context_instance=RequestContext(request))


def course(request, course_id):
    course = Course.objects.get(id=course_id)
    context = {
        'course': course,
        'study_groups': course.studygroup_set.all(),
    }
    return render_to_response('studygroups/course.html', context, context_instance=RequestContext(request))

def signup(request, study_group_id):
    study_group = StudyGroup.objects.get(id=study_group_id)
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            signup = form.save()
            messages.success(request, 'You successfully signed up for a study group!')
            url = reverse('studygroups_course', kwargs={'course_id': study_group.course.id})
            return http.HttpResponseRedirect(url)
    else:
        form = SignupForm(initial={'study_group': study_group.id})

    context = {
        'study_group': study_group,
        'course': study_group.course,
        'form': form
    }
    return render_to_response('studygroups/signup.html', context, context_instance=RequestContext(request))


@login_required
def organize(request):
    context = {
        'courses': Course.objects.all(),
        'study_groups': StudyGroup.objects.all(),
    }
    return render_to_response('studygroups/organize.html', context, context_instance=RequestContext(request))


@login_required
def email(request, study_group_id):
    study_group = StudyGroup.objects.get(id=study_group_id)
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            to = [su.email for su in study_group.studygroupsignup_set.all()]
            send_mail(form.cleaned_data['subject'], form.cleaned_data['body'], settings.DEFAULT_FROM_EMAIL, to, fail_silently=False)
            messages.success(request, 'Email successfully sent')

            # TODO send SMS
            try:
                client = twilio.rest.TwilioRestClient(
                    settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN 
                )
                tos = [su.mobile for su in study_group.studygroupsignup_set.all() if len(su.mobile) > 0]
                for to in tos: 
                    try:
                        message = client.messages.create(
                            body=form.cleaned_data['sms_body'],
                            to=to,
                            from_=settings.TWILIO_NUMBER
                        )
                    except twilio.TwilioRestException as e:
                        messages.warning(request, 'Could not send SMS to ' + to)

            except twilio.TwilioRestException as e:
                messages.error(request, 'Something went wrong while sending an SMS')

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

