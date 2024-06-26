from celery import shared_task
from twilio.base.exceptions import TwilioRestException
from email.mime.text import MIMEText

from django.conf import settings
from django.utils import timezone
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.db.models import Count
from django.db.models import Q
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models import F, Case, When, Value, Sum, IntegerField
from django.db.models.expressions import RawSQL


from studygroups.models import StudyGroup, Meeting, Reminder, Team, TeamMembership, Application
from studygroups.models import Course
from studygroups.models import weekly_update_data
from studygroups.models import community_digest_data
from studygroups.models import get_study_group_organizers
from studygroups.models import get_json_response
from studygroups import charts
from studygroups.sms import send_message
from studygroups.utils import render_to_string_ctx
from studygroups.email_helper import render_email_templates
from studygroups.email_helper import render_html_with_css
from .utils import html_body_to_text
from .utils import use_language
from .ics import make_meeting_ics

import datetime
import logging
import pytz
import os
import re
import dateutil.parser
import tempfile
import csv
import json
import io
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def _send_facilitator_survey(study_group):
    path = reverse('studygroups_facilitator_survey', kwargs={'study_group_uuid': study_group.uuid})
    base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
    survey_url = base_url + path

    context = {
        'study_group': study_group,
        'show_dash_link': True,
        'survey_url': survey_url,
        'course_title': study_group.course.title,
        'study_group_name': study_group.name,
    }

    timezone.deactivate()
    subject, txt, html = render_email_templates(
        'studygroups/email/facilitator_survey',
        context
    )
    to = [f.user.email for f in study_group.facilitator_set.all()]
    cc = [settings.DEFAULT_FROM_EMAIL]

    message = EmailMultiAlternatives(
        subject,
        txt,
        settings.DEFAULT_FROM_EMAIL,
        to,
        cc=cc
    )
    message.attach_alternative(html, 'text/html')
    message.send()

    study_group.facilitator_survey_sent_at = timezone.now()
    study_group.save()


# If called directly, be sure to activate the current language
def send_facilitator_survey(study_group):
    """ send survey to facilitators 2 days after their last meeting """
    last_meeting = study_group.meeting_set.active().order_by('-meeting_date', '-meeting_time').first()
    if not last_meeting:
        return
    # don't send twice or to facilitator that has already responded to a survey
    if study_group.facilitator_survey_sent_at or study_group.facilitatorsurveyresponse_set.count():
        return
    now = timezone.now()
    six_weeks_ago = now - datetime.timedelta(days=42)
    time_to_send = last_meeting.meeting_datetime() + datetime.timedelta(days=2)

    if six_weeks_ago < time_to_send and time_to_send < now:
        _send_facilitator_survey(study_group)


def _send_learner_survey(application):
    """ send email to learner with link to survey, if goal is specified, also ask if they
    achieved their goal """
    learner_goal = application.get_signup_questions().get('goals', None)
    base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
    path = reverse(
        'studygroups_learner_survey',
        kwargs={'study_group_uuid': application.study_group.uuid}
    )
    querystring = '?learner={}'.format(application.uuid)
    survey_url = base_url + path + querystring

    context = {
        'learner_name': application.name,
        'learner_goal': learner_goal,
        'survey_url': survey_url
    }

    subject, txt, html = render_email_templates(
        'studygroups/email/learner_survey',
        context
    )

    to = [application.email]
    notification = EmailMultiAlternatives(
        subject.strip(),
        txt,
        settings.DEFAULT_FROM_EMAIL,
        to,
        reply_to=[facilitator.user.email for facilitator in application.study_group.facilitator_set.all()]
    )
    notification.attach_alternative(html, 'text/html')
    notification.send()


# send an hour before the last meeting
def send_learner_surveys(study_group):
    if study_group.language != 'en':
        # NOTE surveys only supported in English
        return

    if study_group.learner_survey_sent_at:
        return

    last_meeting = study_group.last_meeting()
    if not last_meeting:
        return

    time_to_send = last_meeting.meeting_datetime() - datetime.timedelta(hours=1)

    now = timezone.now()
    three_weeks_ago = now - datetime.timedelta(days=21)

    if three_weeks_ago < time_to_send and time_to_send < now:
        applications = study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')
        study_group.learner_survey_sent_at = now
        study_group.save()
        timezone.deactivate()
        for application in applications:
            _send_learner_survey(application)


def send_meeting_reminder(reminder):
    to = [su.email for su in reminder.study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')]
    sender = 'P2PU <{0}>'.format(settings.DEFAULT_FROM_EMAIL)

    for email in to:
        # activate correct language
        with use_language(reminder.study_group.language):
            yes_link = reminder.study_group_meeting.rsvp_yes_link(email)
            no_link = reminder.study_group_meeting.rsvp_no_link(email)
            application = reminder.study_group.application_set.active().filter(email__iexact=email).first()
            unsubscribe_link = application.unapply_link()
            email_body = reminder.email_body
            email_body = re.sub(r'RSVP_YES_LINK', yes_link, email_body)
            email_body = re.sub(r'RSVP_NO_LINK', no_link, email_body)

            context = {
                "reminder": reminder,
                "learning_circle": reminder.study_group,
                "message": email_body,
                "rsvp_yes_link": yes_link,
                "rsvp_no_link": no_link,
                "unsubscribe_link": unsubscribe_link,
                "event_meta": True,
            }
            html_body = render_to_string_ctx('studygroups/email/learner_meeting_reminder.html', context)
            text_body = html_body_to_text(html_body)
        try:
            reminder_email = EmailMultiAlternatives(
                reminder.email_subject.strip('\n'),
                text_body,
                sender,
                [email],
                reply_to=[facilitator.user.email for facilitator in reminder.study_group.facilitator_set.all()]
            )
            reminder_email.attach_alternative(html_body, 'text/html')
            # attach icalendar event
            if reminder.study_group.attach_ics:
                ical = make_meeting_ics(reminder.study_group_meeting)
                part = MIMEText(ical, 'calendar')
                part.add_header('Filename', 'shifts.ics')
                part.add_header('Content-Disposition', 'attachment; filename=lc.ics')
                reminder_email.attach(part)
            reminder_email.send()
        except Exception as e:
            # TODO - this swallows any exception in the code
            logger.exception('Could not send email to ', email, exc_info=e)

    # Send to facilitator without RSVP & unsubscribe links
    try:
        base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
        path = reverse('studygroups_view_study_group', kwargs={'study_group_id': reminder.study_group.id})
        dashboard_link = base_url + path
        email_body = re.sub(r'RSVP_YES_LINK', dashboard_link, reminder.email_body)
        email_body = re.sub(r'RSVP_NO_LINK', dashboard_link, email_body)

        context = {
            "facilitator_names": reminder.study_group.facilitators_display(),
            "show_dash_link": True,
            "reminder": reminder,
            "message": email_body,
        }

        subject, text_body, html_body = render_email_templates(
            'studygroups/email/facilitator_meeting_reminder',
            context
        )
        reminder_email = EmailMultiAlternatives(
            subject,
            text_body,
            sender,
            [facilitator.user.email for facilitator in reminder.study_group.facilitator_set.all()]
        )
        reminder_email.attach_alternative(html_body, 'text/html')
        reminder_email.send()

    except Exception as e:
        logger.exception('Could not send email to facilitator', exc_info=e) # TODO - Exception masks other errors!


# If called directly, be sure to activate language to use for constructing URLs
# Failed text delivery won't case this function to fail, simply log an error
def send_reminder(reminder):
    # mark it as sent, we don't retry any failures
    reminder.sent_at = timezone.now()
    reminder.save()

    to = [su.email for su in reminder.study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')]
    if reminder.study_group_meeting:
        send_meeting_reminder(reminder)
    else:
        context = {
            "reminder": reminder,
            "facilitator_message": reminder.email_body,
        }
        # activate learning circle language
        with use_language(reminder.study_group.language):
            subject = render_to_string_ctx(
                'studygroups/email/facilitator_message-subject.txt',
                context
            ).strip('\n')
            html_body = render_html_with_css(
                'studygroups/email/facilitator_message.html',
                context
            )
            text_body = html_body_to_text(html_body)
        to += [facilitator.user.email for facilitator in reminder.study_group.facilitator_set.all()]
        sender = 'P2PU <{0}>'.format(settings.DEFAULT_FROM_EMAIL)
        try:
            reminder_email = EmailMultiAlternatives(
                reminder.email_subject.strip('\n'),
                text_body,
                sender,
                [],
                bcc=to,
                reply_to=[facilitator.user.email for facilitator in reminder.study_group.facilitator_set.all()]
            )
            reminder_email.attach_alternative(html_body, 'text/html')
            reminder_email.send()
        except Exception as e:
            logger.exception('Could not send reminder to whole study group', exc_info=e)

    # send SMS
    if reminder.sms_body != '':
        applications = reminder.study_group.application_set.active().filter(accepted_at__isnull=False).exclude(mobile='')
        applications = applications.filter(mobile_opt_out_at__isnull=True)
        tos = [su.mobile for su in applications]
        for to in tos:
            try:
                send_message(to, reminder.sms_body)
            except TwilioRestException as e:
                logger.exception("Could not send text message to %s", to, exc_info=e)


def _send_meeting_wrapup(meeting):
    study_group = meeting.study_group
    context = {
        'study_group': study_group,
        'meeting': meeting,
        'is_last_meeting': meeting == study_group.last_meeting(),
    }
    subject = render_to_string_ctx('studygroups/email/facilitator_meeting_wrapup-subject.txt', context).strip('\n')
    html_body = render_to_string_ctx('studygroups/email/facilitator_meeting_wrapup.html', context)
    text_body = html_body_to_text(html_body)
    message = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to=[facilitator.user.email for facilitator in study_group.facilitator_set.all()]
    )
    message.attach_alternative(html_body, 'text/html')
    try:
        message.send()
    except Exception as e:
        logger.exception('Could not send meeting change notification', exc_info=e)
    meeting.wrapup_sent_at = timezone.now()
    meeting.save()


def send_meeting_wrapup(study_group):
    now = timezone.now()  
    # convert to correct timezone first so that .date and .time is correct
    tz = pytz.timezone(study_group.timezone)
    now = now.astimezone(tz)
    
    previous_meeting = study_group.meeting_set.active().filter(
        meeting_date__lte=now.date(), meeting_time__lt=now.time()
    ).order_by('-meeting_date', '-meeting_time').first()

    if not previous_meeting or previous_meeting.wrapup_sent_at:
        return

    # send if time to send is in the past, but not yet more than 1 day
    # send_at falls between yesterday this time and now
    # ie. don't send for old meetings
    send_at = previous_meeting.meeting_datetime() + datetime.timedelta(minutes=study_group.duration)
    if now - datetime.timedelta(days=1) < send_at and send_at < now :
        _send_meeting_wrapup(previous_meeting)


@shared_task
def send_meeting_wrapups():
    now = timezone.now()
    cutoff = now - datetime.timedelta(days=2)
    study_groups = StudyGroup.objects.published().filter(end_date__gte=cutoff.date())
    for sg in study_groups:
        send_meeting_wrapup(sg)


@shared_task
def send_meeting_change_notification(meeting_id, old_meeting_datetime):
    meeting = Meeting.objects.get(pk=meeting_id)
    study_group = meeting.study_group
    to = [su.email for su in study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')]
    context = {
        'old_meeting_datetime': dateutil.parser.parse(old_meeting_datetime),
        'meeting': meeting,
        'learning_circle': study_group,
    }

    with use_language(study_group.language), timezone.override(pytz.timezone(study_group.timezone)):
        subject = render_to_string_ctx('studygroups/email/meeting_changed-subject.txt', context).strip('\n')
        html_body = render_to_string_ctx('studygroups/email/meeting_changed.html', context)
        text_body = html_body_to_text(html_body)
        sms_body = render_to_string_ctx('studygroups/email/meeting_changed-sms.txt', context).strip('\n')

    notification = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        bcc=to
    )
    notification.attach_alternative(html_body, 'text/html')
    try:
        notification.send()
    except Exception as e:
        logger.exception('Could not send meeting change notification', exc_info=e)

    applications = study_group.application_set.active().filter(accepted_at__isnull=False).exclude(mobile='')
    applications = applications.filter(mobile_opt_out_at__isnull=True)
    tos = [su.mobile for su in applications]
    for to in tos:
        try:
            send_message(to, sms_body)
        except TwilioRestException as e:
            logger.exception("Could not send text message to %s", to, exc_info=e)


def send_team_invitation_email(team, email, organizer):
    """ Send email to new or existing facilitators """
    """ organizer should be a User object """
    user_qs = User.objects.filter(email__iexact=email)
    context = {
        "team": team,
        "organizer": organizer,
    }

    if user_qs.count() == 0:
        # invite user to join
        subject = render_to_string_ctx('studygroups/email/new_facilitator_invite-subject.txt', context).strip('\n')
        html_body = render_html_with_css('studygroups/email/new_facilitator_invite.html', context)
        text_body = render_to_string_ctx('studygroups/email/new_facilitator_invite.txt', context)
    else:
        context['user'] = user_qs.get()
        subject = render_to_string_ctx('studygroups/email/team_invite-subject.txt', context).strip('\n')
        html_body = render_html_with_css('studygroups/email/team_invite.html', context)
        text_body = render_to_string_ctx('studygroups/email/team_invite.txt', context)

    to = [email]
    from_ = organizer.email

    msg = EmailMultiAlternatives(subject, text_body, from_, to)
    msg.attach_alternative(html_body, 'text/html')
    msg.send()


def send_weekly_update():
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = today - datetime.timedelta(days=today.weekday() + 7) #start of previous week
    end_time = start_time + datetime.timedelta(days=7)

    context = {
        'start_time': start_time,
        'end_time': end_time,
        'email': True,
    }

    for team in Team.objects.all():
        report_context = weekly_update_data(today, team)
        # If there wasn't any activity during this period discard the update
        if report_context['active'] is False:
            continue
        report_context.update(context)
        timezone.activate(pytz.timezone(settings.TIME_ZONE)) #TODO not sure what this influences anymore?
        translation.activate(settings.LANGUAGE_CODE)
        html_body = render_html_with_css('studygroups/email/weekly-update.html', report_context)
        text_body = html_body_to_text(html_body)
        timezone.deactivate()

        to = [member.user.email for member in team.teammembership_set.active().filter(weekly_update_opt_in=True)]
        update = EmailMultiAlternatives(
            _('Weekly team update for {}'.format(team.name)),
            text_body,
            settings.DEFAULT_FROM_EMAIL,
            to=to,
            cc=[settings.TEAM_MANAGER_EMAIL]
        )
        update.attach_alternative(html_body, 'text/html')
        update.send()

    # send weekly update to staff
    report_context = weekly_update_data(today)
    report_context.update(context)
    report_context['staff_update'] = True
    timezone.activate(pytz.timezone(settings.TIME_ZONE))
    translation.activate(settings.LANGUAGE_CODE)
    html_body = render_html_with_css('studygroups/email/weekly-update.html', report_context)
    text_body = html_body_to_text(html_body)
    timezone.deactivate()

    to = [o.email for o in User.objects.filter(is_staff=True)]
    update = EmailMultiAlternatives(
        _('Weekly learning circles update'),
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to
    )
    update.attach_alternative(html_body, 'text/html')
    update.send()


@shared_task
def send_community_digest(start_date, end_date):
    context = community_digest_data(start_date, end_date)

    chart_data = {
        "meetings_chart": charts.LearningCircleMeetingsChart(end_date.date()).generate(output="png"),
        "countries_chart": charts.LearningCircleCountriesChart(start_date.date(), end_date.date()).generate(output="png"),
        "top_topics_chart": charts.TopTopicsChart(end_date.date(), context['studygroups_that_met']).generate(output="png"),
    }

    context.update(chart_data)

    subject = render_to_string_ctx('studygroups/email/community_digest-subject.txt', context)
    html_body = render_html_with_css('studygroups/email/community_digest.html', context)
    text_body = html_body_to_text(html_body)
    to = [settings.COMMUNITY_DIGEST_EMAIL]

    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, to)
    msg.attach_alternative(html_body, 'text/html')
    msg.send()


@shared_task
def send_reminders():
    """ Send meeting reminders """
    # TODO rename to check_reminders_to_send
    
    # make sure both the StudyGroup and Meeting is still available
    reminders = Reminder.objects.filter(
        sent_at__isnull=True,
        study_group__in=StudyGroup.objects.published(),
        study_group_meeting__in=Meeting.objects.active()
    )
    for reminder in reminders:
        # send the reminder if now is between when it should be sent and when the meeting happens
        meeting_datetime = reminder.study_group_meeting.meeting_datetime()
        send_at = reminder.send_at()
        now = timezone.now() # NOTE: don't move now up, send_at() also call timezone.now()
        if send_at < now and now < meeting_datetime:
            send_reminder(reminder)


@shared_task
def weekly_update():
    # Create a report for the previous week
    send_weekly_update()


@shared_task
def send_all_learner_surveys():
    for study_group in StudyGroup.objects.published().filter(learner_survey_sent_at__isnull=True):
        translation.activate(settings.LANGUAGE_CODE)
        send_learner_surveys(study_group)


@shared_task
def send_all_facilitator_surveys():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        send_facilitator_survey(study_group)


@shared_task
def send_out_community_digest():
    translation.activate(settings.LANGUAGE_CODE)
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    iso_week = today.isocalendar()[1]
    end_date = today
    start_date = end_date - datetime.timedelta(days=21)

    if iso_week % 3 == 0:
        send_community_digest(start_date, end_date)


@shared_task
def refresh_instagram_token():
    """ Refresh long-lived user access token for Instagram Basic Display API """
    """ https://developers.facebook.com/docs/instagram-basic-display-api/reference/refresh_access_token """
    url = "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token={}".format(settings.INSTAGRAM_TOKEN)
    response = get_json_response(url)
    new_token = response.get("access_token", None)
    request_error = response.get("error", None)

    if new_token:
        os.environ["INSTAGRAM_TOKEN"] = new_token
        logger.info("Set refreshed Instagram token to os.environ.INSTAGRAM_TOKEN")
    elif request_error:
        logger.error('Could not refresh Instagram token: {}'.format(request_error.get("message")))
    else:
        logger.error('Could not refresh Instagram token: {}'.format(response))


@shared_task
def anonymize_signups():
    # find all signups where the learning circle ended more than 3 months ago
    three_months_ago = timezone.now() - datetime.timedelta(days=90)
    # TODO for now only EU teams
    eu_teams_ids = [33, 34, 35, 36, 37]
    facilitators = TeamMembership.objects.active().filter(team_id__in=eu_teams_ids).values_list('user', flat=True)
    applications = Application.objects.filter(
        study_group__end_date__lt=three_months_ago,
        anonymized=False,
        communications_opt_in=False,
        study_group__facilitator__in=facilitators
    )

    for application in applications:
        application.anonymize()


@shared_task
def send_cofacilitator_email(study_group_id, user_id, actor_user_id):
    user = User.objects.get(pk=user_id)
    actor = User.objects.get(pk=actor_user_id)
    context = {
        "study_group": StudyGroup.objects.get(pk=study_group_id),
        "facilitator": user,
        "actor": actor,
    }
    subject = render_to_string_ctx('studygroups/email/facilitator_added-subject.txt', context).strip('\n')
    html_body = render_html_with_css('studygroups/email/facilitator_added.html', context)
    text_body = html_body_to_text(html_body)
    to = [user.email]

    msg = EmailMultiAlternatives(
        subject, 
        text_body, 
        settings.DEFAULT_FROM_EMAIL, 
        to,
        reply_to=[actor.email])
    msg.attach_alternative(html_body, 'text/html')
    msg.send()


@shared_task
def send_cofacilitator_removed_email(study_group_id, user_id, actor_user_id):
    user = User.objects.get(pk=user_id)
    actor = User.objects.get(pk=actor_user_id)
    context = {
        "study_group": StudyGroup.objects.get(pk=study_group_id),
        "facilitator": user,
        "actor": actor,
    }
    subject = render_to_string_ctx('studygroups/email/facilitator_removed-subject.txt', context).strip('\n')
    html_body = render_html_with_css('studygroups/email/facilitator_removed.html', context)
    text_body = html_body_to_text(html_body)
    to = [user.email]

    msg = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to,
        reply_to=[actor.email]
    )
    msg.attach_alternative(html_body, 'text/html')
    msg.send()


def upload_to_s3(file_obj, export_name):
    ts = timezone.now().utcnow().isoformat()
    filename = '{}-{}.csv'.format(export_name, ts)
    key = '/'.join(['learning-circles', 'exports', filename])
    bucket = settings.P2PU_RESOURCES_AWS_BUCKET

    s3 = boto3.client('s3', aws_access_key_id=settings.P2PU_RESOURCES_AWS_ACCESS_KEY, aws_secret_access_key=settings.P2PU_RESOURCES_AWS_SECRET_KEY)
    response = s3.upload_fileobj(
        file_obj, bucket, key,
    )
    file_obj.close()

    try:
        presigned_url = s3.generate_presigned_url(
            'get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=1800
        )
    except ClientError as e:
        logger.error(e)
        return None

    return { "presigned_url": presigned_url, "export_name": export_name, "s3_key": key}


@shared_task
def export_signups(user_id):
    """ user_id - the person requesting the export """

    object_list = Application.objects.all().prefetch_related('study_group', 'study_group__course')

    signup_questions = ['support', 'goals', 'computer_access']
    field_names = [
        'id', 'uuid', 'study group id', 'study group uuid', 'study group name', 'course',
        'location', 'name', 'email', 'mobile', 'signed up at'
    ] + signup_questions + ['use_internet', 'survey completed', 'communications opt-in']

    temp_file = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(temp_file))
    writer.writerow(field_names)
    for signup in object_list:
        signup_data = json.loads(signup.signup_questions)
        digital_literacy = 'n/a'
        if signup_data.get('use_internet'):
            digital_literacy = dict(Application.DIGITAL_LITERACY_CHOICES)[signup_data.get('use_internet')]
        writer.writerow(
            [
                signup.id,
                signup.uuid,
                signup.study_group_id,
                signup.study_group.uuid,
                signup.study_group.name,
                signup.study_group.course.title,
                signup.study_group.venue_name,
                signup.name,
                signup.email,
                signup.mobile,
                signup.created_at,
            ] +
            [ signup_data.get(key, 'n/a') for key in signup_questions ] +
            [
                digital_literacy,
                'yes' if signup.learnersurveyresponse_set.count() else 'no'
            ] +
            [ signup.communications_opt_in ]
        )

    temp_file.seek(0)

    return upload_to_s3(temp_file, 'signups')
    

@shared_task
def export_users():
    learning_circles = StudyGroup.objects.select_related('course').published().filter(facilitator__user_id=OuterRef('pk')).order_by('-start_date')
    users = User.objects.all().annotate(
        learning_circle_count=Sum(
            Case(
                When(
                    facilitator__study_group__deleted_at__isnull=True,
                    facilitator__study_group__draft=False,
                    then=Value(1),
                    facilitator__user__id=F('id')
                ),
                default=Value(0), output_field=IntegerField()
            )
        )
    ).annotate(
        last_learning_circle_date=Subquery(learning_circles.values('start_date')[:1]),
        last_learning_circle_name=Subquery(learning_circles.values('name')[:1]),
        last_learning_circle_course=Subquery(learning_circles.values('course__title')[:1]),
        last_learning_circle_venue=Subquery(learning_circles.values('venue_name')[:1])
    )

    temp_file = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(temp_file))

    field_names = ['name',
        'email',
        'date joined',
        'last login',
        'communication opt-in',
        'learning circles run',
        'last learning circle date',
        'last learning cirlce name',
        'last learning circle course',
        'last learning circle venue',
    ]
    writer.writerow(field_names)
    for user in users:
        data = [
            ' '.join([user.first_name, user.last_name]),
            user.email,
            user.date_joined,
            user.last_login,
            user.profile.communication_opt_in if user.profile else False,
            user.learning_circle_count,
            user.last_learning_circle_date,
            user.last_learning_circle_name,
            user.last_learning_circle_course,
            user.last_learning_circle_venue,
        ]
        writer.writerow(data)

    temp_file.seek(0)

    return upload_to_s3(temp_file, 'facilitators')


@shared_task
def export_learning_circles():
    object_list = StudyGroup.objects.all().prefetch_related('course', 'facilitator_set', 'meeting_set').annotate(
        learning_circle_number=RawSQL("RANK() OVER(PARTITION BY created_by_id ORDER BY created_at ASC)", [])
    )

    temp_file = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(temp_file))

    field_names = [
        'id',
        'uuid',
        'name',
        'date created',
        'date deleted',
        'draft',
        'course id',
        'course title',
        'created by',
        'created by email',
        'learning_circle_number',
        'location',
        'city',
        'time',
        'day',
        'last meeting',
        'first meeting',
        'signups',
        'team',
        'facilitator survey',
        'facilitator survey completed',
        'learner survey',
        'learner survey responses',
        'did not happen',
        'facilitator count',
    ]
    writer.writerow(field_names)
    for sg in object_list:
        data = [
            sg.pk,
            sg.uuid,
            sg.name,
            sg.created_at,
            sg.deleted_at,
            'yes' if sg.draft else 'no',
            sg.course.id,
            sg.course.title,
            ' '.join([sg.created_by.first_name, sg.created_by.last_name]),
            sg.created_by.email,
            sg.learning_circle_number,
            ' ' .join([sg.venue_name, sg.venue_address]),
            sg.city,
            sg.meeting_time,
            sg.day(),
        ]
        if sg.meeting_set.active().last():
            data += [sg.meeting_set.active().order_by('meeting_date', 'meeting_time').last().meeting_date]
        elif sg.deleted_at:
            data += [sg.start_date]
        else:
            data += ['']

        if sg.meeting_set.active().first():
            data += [sg.meeting_set.active().order_by('meeting_date', 'meeting_time').first().meeting_date]
        elif sg.deleted_at:
            data += [sg.end_date]
        else:
            data += ['']

        data += [sg.application_set.active().count()]

        if sg.team:
            data += [sg.team.name]
        else:
            data += ['']

        base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
        facilitator_survey =  '{}{}'.format(
            base_url,
            reverse('studygroups_facilitator_survey', args=(sg.uuid,))
        )
        data += [facilitator_survey]
        data += ['yes' if sg.facilitatorsurveyresponse_set.count() else 'no']
        learner_survey = '{}{}'.format(
            base_url,
            reverse('studygroups_learner_survey', args=(sg.uuid,))
        )
        data += [learner_survey]
        data += [sg.learnersurveyresponse_set.count()]
        data += [sg.did_not_happen]
        data += [sg.facilitator_set.count()]

        writer.writerow(data)

    temp_file.seek(0)
    return upload_to_s3(temp_file, 'learning-circles')


@shared_task
def export_courses():
    team_membership = TeamMembership.objects.active().filter(user=OuterRef('created_by'))
    object_list = Course.objects.active()\
        .filter(studygroup__deleted_at__isnull=True, studygroup__draft=False)\
        .filter(facilitatorguide__deleted_at__isnull=True)\
        .annotate(lc_count=Count('studygroup', distinct=True))\
        .annotate(active_lc_count=Count('studygroup', distinct=True, filter=Q(studygroup__end_date__gte=timezone.now())))\
        .annotate(facilitator_guide_count=Count('facilitatorguide', distinct=True))\
        .annotate(team_name=Subquery(team_membership.values('team__name')[:1]))\
        .select_related('created_by')

    temp_file = io.BytesIO()
    writer = csv.writer(io.TextIOWrapper(temp_file))

    db_fields = [
        'id',
        'title',
        'provider',
        'link',
        'caption',
        'on_demand',
        'keywords',
        'language',
        'created_by',
        'unlisted',
        'license',
        'created_at',
        'lc_count',
        'active_lc_count',
        'facilitator_guide_count',
        'team_name',
    ]
    writer.writerow(db_fields)
    for obj in object_list:
        data = [
            getattr(obj, field) for field in db_fields
        ]
        writer.writerow(data)

    temp_file.seek(0)
    return upload_to_s3(temp_file, 'courses')

