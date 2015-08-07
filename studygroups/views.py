from datetime import datetime

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django import http
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from studygroups.models import Course, Location, StudyGroup, Application, Reminder
from studygroups.models import send_reminder
from studygroups.forms import ApplicationForm, MessageForm
from studygroups.sms import send_message


def landing(request):
    courses = Course.objects.all().order_by('key')

    for course in courses:
        course.studygroups = course.studygroup_set.all()

    context = {
        'courses': courses,
        'interest': {
            'courses': [
                'Computer programming',
                'Writing skills',
                'How to Succeed at Interviews',
                'Managing Your Money',
                'High-Impact Business Writing',
                'Public Speaking',
                'Introduction to Psychology',
                'Principles of Microeconomics',
                'Single Variable Calculus',
            ],
            'primary_locations': ['Harold Washington Library Center', 'Bezazian', 'Edgewater', 'Daley, Richard J.-Bridgeport', ],
            'secondary_locations': [
                'Lincoln Park', 'Lincoln Belmont', 'Merlo', 'Uptown', 'West Town', 'Near North', 'Roden',
                'Mount Greenwood', 'Oriole Park', 'Rogers Park', 'Humboldt Park', 'Logan Square',
                'Bucktown-Wicker Park', 'Independence', 'Edgebrook', 'Northtown', 'Roosevelt', 
                'Budlong Woods',
                'Wrightwood-Ashburn',
                'Scottsdale',
                'Clearing',
                'Garfield Ridge',
                'Dunning',
                'West Belmont',
                'Austin-Irving',
                'Mayfair', 
                'Jefferson Park',
                'King',
                'Chinatown', 
                'Portage-Cragin',
                'Daley, Richard M.-W Humboldt',
                'Manning',
                'West Lawn',
                'Chicago Lawn',
                'Hall', 
                'Blackstone',
                'Hegewisch',
                'North Pulaski',
                'North Austin',
                'Walker',
                'West Pullman',
                'Beverly',
                'Brighton Park',
                'Archer Heights', 
                'Little Village',
                'Toman',
                'Douglass',
                'Lozano',
                'Vodak-East Side',
                'South Chicago',
                'Jeffery Manor', 
                'Avalon',
                'South Shore',
                'Pullman',
                'West Chicago Avenue',
                'Sherman Park',
                'Back of the Yards',
                'Chicago Bee',
                'McKinley Park',
                'Whitney M. Young, Jr.',
                'Greater Grand Crossing',
                'Coleman',
                'Altgeld', 
                'Legler',
                'Kelly', 
                'Thurgood Marshall',
                'Brainerd',
                'West Englewood',
            ],
        },
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
        'locations': Location.objects.all(),
        'facilitators': Group.objects.get(name='facilitators').user_set.all()
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
        form = MessageForm(request.POST)
        if form.is_valid():
            reminder = form.save()
            try:
                send_reminder(reminder)
                messages.success(request, 'Email successfully sent')
            except Exception as e:
                messages.error(request, 'An error occured while sending group message.')

            url = reverse('studygroups_organize')
            return http.HttpResponseRedirect(url)
    else:
        form = MessageForm(initial={'study_group': study_group})

    context = {
        'study_group': study_group,
        'course': study_group.course,
        'form': form
    }
    return render_to_response('studygroups/email.html', context, context_instance=RequestContext(request))


def messages_edit(request, study_group_id, message_id):
    study_group = StudyGroup.objects.get(id=study_group_id)
    reminder = Reminder.objects.get(id=message_id)
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
    send_mail(subject, message, settings.SERVER_EMAIL, to, fail_silently=False)
    return http.HttpResponse(status=200)
