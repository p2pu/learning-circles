from celery import shared_task
from twilio.base.exceptions import TwilioRestException
from email.mime.text import MIMEText

from django.conf import settings
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse

from studygroups.models import StudyGroup, Meeting, Reminder, Team, TeamMembership
from studygroups.models import report_data
from studygroups.models import community_digest_data
from studygroups.models import get_study_group_organizers
from studygroups import charts
from studygroups.sms import send_message
from studygroups.email_helper import render_email_templates
from studygroups.email_helper import render_html_with_css
from .utils import html_body_to_text
from .events import make_meeting_ics

import datetime
import logging
import pytz


logger = logging.getLogger(__name__)


def generate_reminder(study_group):
    now = timezone.now()
    next_meeting = study_group.next_meeting()
    if next_meeting and next_meeting.meeting_datetime() - now < datetime.timedelta(days=4):
        # check if a notifcation already exists for this meeting
        if not Reminder.objects.filter(study_group=study_group, study_group_meeting=next_meeting).exists():
            reminder = Reminder()
            reminder.study_group = study_group
            reminder.study_group_meeting = next_meeting
            context = {
                'facilitator': study_group.facilitator,
                'study_group': study_group,
                'next_meeting': next_meeting,
                'reminder': reminder,
                'protocol': 'https',
                'domain': settings.DOMAIN,
            }
            previous_meeting = study_group.meeting_set.filter(meeting_date__lt=next_meeting.meeting_date).order_by('meeting_date').last()
            if previous_meeting and previous_meeting.feedback_set.first():
                context['feedback'] = previous_meeting.feedback_set.first()
            timezone.activate(pytz.timezone(study_group.timezone))
            # TODO do I need to activate a locale?
            reminder.email_subject = render_to_string(
                'studygroups/email/reminder-subject.txt',
                context
            ).strip('\n')
            reminder.email_body = render_to_string(
                'studygroups/email/reminder.txt',
                context
            )
            reminder.sms_body = render_to_string(
                'studygroups/email/sms.txt',
                context
            )
            # TODO - handle SMS reminders that are too long
            if len(reminder.sms_body) > 160:
                logger.error('SMS body too long: ' + reminder.sms_body)
            reminder.sms_body = reminder.sms_body[:160]
            reminder.save()

            facilitator_notification_subject = 'A reminder for {0} was generated'.format(study_group.course.title)
            facilitator_notification_html = render_html_with_css(
                'studygroups/email/reminder_notification.html',
                context
            )
            facilitator_notification_txt = render_to_string(
                'studygroups/email/reminder_notification.txt',
                context
            )
            timezone.deactivate()
            to = [study_group.facilitator.email]
            notification = EmailMultiAlternatives(
                facilitator_notification_subject,
                facilitator_notification_txt,
                settings.DEFAULT_FROM_EMAIL,
                to
            )
            notification.attach_alternative(facilitator_notification_html, 'text/html')
            notification.send()


# If called directly, be sure to activate the current language
# Should be called every hour at :30
def send_facilitator_survey(study_group):
    """ send survey to all facilitators two days before their second to last meeting """
    now = timezone.now()
    end_of_window = now.replace(minute=0, second=0, microsecond=0)
    start_of_window = end_of_window - datetime.timedelta(hours=1)

    last_two_meetings = study_group.meeting_set.active().order_by('-meeting_date', '-meeting_time')[:2]
    time_to_send = None
    if last_two_meetings.count() == 2:
        penultimate_meeting = last_two_meetings[1]
        time_to_send = penultimate_meeting.meeting_datetime() - datetime.timedelta(days=2, hours=1)

    if time_to_send and time_to_send > start_of_window and time_to_send <= end_of_window:
        facilitator_name = study_group.facilitator.first_name
        path = reverse('studygroups_facilitator_survey', kwargs={'study_group_id': study_group.id})
        domain = 'https://{}'.format(settings.DOMAIN)
        survey_url = domain + path

        context = {
            "facilitator": study_group.facilitator,
            'facilitator_name': facilitator_name,
            'survey_url': survey_url,
            'course_title': study_group.course.title,
        }

        timezone.deactivate()
        subject, txt, html = render_email_templates(
            'studygroups/email/facilitator-survey',
            context
        )
        to = [study_group.facilitator.email]
        cc = [settings.DEFAULT_FROM_EMAIL]

        notification = EmailMultiAlternatives(
            subject,
            txt,
            settings.DEFAULT_FROM_EMAIL,
            to,
            cc=cc
        )
        notification.attach_alternative(html, 'text/html')
        notification.send()


# send survey reminder to all facilitators two days before the last meeting
# should be called every hour at :30
def send_facilitator_survey_reminder(study_group):
    now = timezone.now()
    end_of_window = now.replace(minute=0, second=0, microsecond=0)
    start_of_window = end_of_window - datetime.timedelta(hours=1)

    last_meeting = study_group.meeting_set.active().order_by('-meeting_date', '-meeting_time').first()
    time_to_send = last_meeting.meeting_datetime() - datetime.timedelta(days=2)

    if time_to_send and time_to_send > start_of_window and time_to_send <= end_of_window:
        timezone.deactivate()

        facilitator_name = study_group.facilitator.first_name
        facilitator_survey_path = reverse(
            'studygroups_facilitator_survey',
            kwargs={'study_group_id': study_group.id}
        )
        learner_survey_path = reverse(
            'studygroups_learner_survey',
            kwargs={'study_group_uuid': study_group.uuid}
        )
        report_path = reverse('studygroups_final_report', kwargs={'study_group_id': study_group.id})
        domain = 'https://{}'.format(settings.DOMAIN)
        facilitator_survey_url = domain + facilitator_survey_path
        learner_survey_url = domain + learner_survey_path
        report_url = domain + report_path
        learners_without_survey_responses = study_group.application_set.active().filter(goal_met=None)

        context = {
            "facilitator": study_group.facilitator,
            'facilitator_name': facilitator_name,
            'learner_survey_url': learner_survey_url,
            'facilitator_survey_url': facilitator_survey_url,
            'course_title': study_group.course.title,
            'learners_without_survey_responses': learners_without_survey_responses,
            'learner_responses_count': study_group.learnersurveyresponse_set.count(),
            'report_url': report_url,
        }

        if study_group.facilitatorsurveyresponse_set.exists():
            context['facilitator_survey_url'] = None

        if learners_without_survey_responses.count() == 0:
            context['learners_without_survey_responses'] = None

        subject, txt, html = render_email_templates(
            'studygroups/email/facilitator-survey-reminder',
            context
        )
        to = [study_group.facilitator.email]
        cc = [settings.DEFAULT_FROM_EMAIL]

        notification = EmailMultiAlternatives(
            subject,
            txt,
            settings.DEFAULT_FROM_EMAIL,
            to,
            cc=cc
        )
        notification.attach_alternative(html, 'text/html')
        notification.send()


# send learning circle report two days after last meeting
# should be called every hour at :30
def send_final_learning_circle_report(study_group):
    now = timezone.now()
    end_of_window = now.replace(minute=0, second=0, microsecond=0)
    start_of_window = end_of_window - datetime.timedelta(hours=1)

    last_meeting = study_group.meeting_set.active().order_by('-meeting_date', '-meeting_time').first()
    time_to_send = last_meeting.meeting_datetime() + datetime.timedelta(days=2)

    if time_to_send and time_to_send > start_of_window and time_to_send <= end_of_window:
        timezone.deactivate()

        learner_goals_chart = charts.LearnerGoalsChart(study_group)
        goals_met_chart = charts.GoalsMetChart(study_group)
        report_path = reverse('studygroups_final_report', kwargs={'study_group_id': study_group.id})
        recipients = study_group.application_set.values_list('email', flat=True)
        organizers = get_study_group_organizers(study_group)
        organizers_emails = [organizer.email for organizer in organizers]
        to = list(recipients) + organizers_emails
        to.append(study_group.facilitator.email)

        context = {
            'study_group': study_group,
            'report_path': report_path,
            'facilitator_name': study_group.facilitator.first_name,
            'registrations': study_group.application_set.active().count(),
            'survey_responses': study_group.learnersurveyresponse_set.count(),
            'learner_goals_chart': learner_goals_chart.generate(output="png"),
            'goals_met_chart': goals_met_chart.generate(output="png"),
        }

        subject = render_to_string('studygroups/email/learning_circle_final_report-subject.txt', context).strip('\n')
        html = render_html_with_css('studygroups/email/learning_circle_final_report.html', context)
        txt = html_body_to_text(html)

        notification = EmailMultiAlternatives(
            subject,
            txt,
            settings.DEFAULT_FROM_EMAIL,
            bcc=to,
            reply_to=[settings.DEFAULT_FROM_EMAIL]
        )
        notification.attach_alternative(html, 'text/html')
        notification.send()


def send_last_week_group_activity(study_group):
    """ send to facilitator when last meeting is in 2 days """
    now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    two_days_from_now = today + datetime.timedelta(days=2)
    last_meeting = study_group.meeting_set.active()\
            .order_by('-meeting_date', '-meeting_time').first()

    if last_meeting and two_days_from_now < last_meeting.meeting_datetime() and last_meeting.meeting_datetime() < two_days_from_now + datetime.timedelta(days=1):

        two_weeks_from_now = today + datetime.timedelta(weeks=2)
        next_study_group = StudyGroup.objects.filter(start_date__gte=two_weeks_from_now).order_by('start_date').first()

        timezone.deactivate()

        context = {
            'next_study_group': next_study_group,
            'facilitator_name': study_group.facilitator.first_name
        }

        if next_study_group:
            next_study_group_start_delta = next_study_group.start_date - today.date()
            weeks_until_start = next_study_group_start_delta.days//7
            context['weeks'] = weeks_until_start
            context['city'] = next_study_group.city
            context['course_title'] = next_study_group.course.title

        subject = render_to_string(
            'studygroups/email/last_week_group_activity-subject.txt',
            context
        ).strip('\n')
        html = render_html_with_css(
            'studygroups/email/last_week_group_activity.html',
            context
        )
        txt = html_body_to_text(html)
        to = [study_group.facilitator.email]

        notification = EmailMultiAlternatives(
            subject,
            txt,
            settings.DEFAULT_FROM_EMAIL,
            to,
            reply_to=[settings.DEFAULT_FROM_EMAIL]
        )
        notification.attach_alternative(html, 'text/html')
        notification.send()


def send_learner_survey(application):
    """ send email to learner with link to survey, if goal is specified, also ask if they
    achieved their goal """
    learner_goal = application.get_signup_questions().get('goals', None)
    domain = 'https://{}'.format(settings.DOMAIN)
    path = reverse(
        'studygroups_learner_survey',
        kwargs={'study_group_uuid': application.study_group.uuid}
    )
    querystring = '?learner={}'.format(application.uuid)
    survey_url = domain + path + querystring

    context = {
        'learner_name': application.name,
        'learner_goal': learner_goal,
        'survey_url': survey_url
    }

    subject, txt, html = render_email_templates(
        'studygroups/email/learner_survey_reminder',
        context
    )

    to = [application.email]
    notification = EmailMultiAlternatives(
        subject.strip(),
        txt,
        settings.DEFAULT_FROM_EMAIL,
        to
    )
    notification.attach_alternative(html, 'text/html')
    notification.send()


# send two days before the second to last meeting
# should be called every hour at :30
def send_learner_surveys(study_group):
    now = timezone.now()
    end_of_window = now.replace(minute=0, second=0, microsecond=0)
    start_of_window = end_of_window - datetime.timedelta(hours=1)

    last_two_meetings = study_group.meeting_set.active().order_by('-meeting_date', '-meeting_time')[:2]
    time_to_send = None
    if last_two_meetings.count() == 2:
        penultimate_meeting = last_two_meetings[1]
        time_to_send = penultimate_meeting.meeting_datetime() - datetime.timedelta(days=2, hours=1)

    if time_to_send and time_to_send > start_of_window and time_to_send <= end_of_window:
        applications = study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')
        timezone.deactivate()

        for application in applications:
            send_learner_survey(application)


def send_meeting_reminder(reminder):
    to = [su.email for su in reminder.study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')]
    sender = 'P2PU <{0}>'.format(settings.DEFAULT_FROM_EMAIL)

    for email in to:
        yes_link = reminder.study_group_meeting.rsvp_yes_link(email)
        no_link = reminder.study_group_meeting.rsvp_no_link(email)
        application = reminder.study_group_meeting.study_group.application_set.active().filter(email__iexact=email).first()
        unsubscribe_link = application.unapply_link()
        context = {
            "reminder": reminder,
            "learning_circle": reminder.study_group,
            "facilitator_message": reminder.email_body,
            "rsvp_yes_link": yes_link,
            "rsvp_no_link": no_link,
            "unsubscribe_link": unsubscribe_link,
            "domain": 'https://{0}'.format(settings.DOMAIN),
            "event_meta": True,
        }
        subject, text_body, html_body = render_email_templates(
            'studygroups/email/learner_meeting_reminder',
            context
        )
        # TODO not using subject
        try:
            reminder_email = EmailMultiAlternatives(
                reminder.email_subject.strip('\n'),
                text_body,
                sender,
                [email],
                reply_to=[reminder.study_group.facilitator.email]
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
            logger.exception('Could not send email to ', email, exc_info=e)
    # Send to organizer without RSVP & unsubscribe links
    try:
        context = {
            "facilitator": reminder.study_group.facilitator,
            "reminder": reminder,
            "facilitator_message": reminder.email_body,
            "domain": 'https://{0}'.format(settings.DOMAIN),
        }
        subject, text_body, html_body = render_email_templates(
            'studygroups/email/facilitator_meeting_reminder',
            context
        )

        reminder_email = EmailMultiAlternatives(
            reminder.email_subject.strip('\n'),
            text_body,
            sender,
            [reminder.study_group.facilitator.email]
        )
        reminder_email.attach_alternative(html_body, 'text/html')
        reminder_email.send()

    except Exception as e:
        logger.exception('Could not send email to ', reminder.study_group.facilitator.email, exc_info=e)


def send_new_studygroup_email(studygroup):
    context = {
        'studygroup': studygroup,
        'facilitator': studygroup.facilitator
    }

    timezone.activate(pytz.timezone(settings.TIME_ZONE))
    translation.activate(settings.LANGUAGE_CODE)
    subject = render_to_string('studygroups/email/new_studygroup_update-subject.txt', context).strip('\n')
    html_body = render_html_with_css('studygroups/email/new_studygroup_update.html', context)
    text_body = html_body_to_text(html_body)
    timezone.deactivate()
    to = [studygroup.facilitator.email]

    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, to)
    msg.attach_alternative(html_body, 'text/html')
    msg.send()


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
            "domain": 'https://{0}'.format(settings.DOMAIN),
            "facilitator": reminder.study_group.facilitator
        }
        subject, text_body, html_body = render_email_templates(
            'studygroups/email/facilitator_message',
            context
        )
        to += [reminder.study_group.facilitator.email]
        sender = 'P2PU <{0}>'.format(settings.DEFAULT_FROM_EMAIL)
        try:
            reminder_email = EmailMultiAlternatives(
                reminder.email_subject.strip('\n'),
                text_body,
                sender,
                [],
                bcc=to,
                reply_to=[reminder.study_group.facilitator.email],
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


def send_team_invitation_email(team, email, organizer):
    """ Send email to new or existing facilitators """
    """ organizer should be a User object """
    user_qs = User.objects.filter(email__iexact=email)
    context = {
        "team": team,
        "organizer": organizer,
        "domain": "learningcircles.p2pu.org"
    }

    if user_qs.count() == 0:
        # invite user to join
        subject = render_to_string('studygroups/email/new_facilitator_invite-subject.txt', context).strip('\n')
        html_body = render_html_with_css('studygroups/email/new_facilitator_invite.html', context)
        text_body = render_to_string('studygroups/email/new_facilitator_invite.txt', context)
    else:
        context['user'] = user_qs.get()
        subject = render_to_string('studygroups/email/team_invite-subject.txt', context).strip('\n')
        html_body = render_html_with_css('studygroups/email/team_invite.html', context)
        text_body = render_to_string('studygroups/email/team_invite.txt', context)

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
        'protocol': 'https',
        'domain': settings.DOMAIN,
    }

    for team in Team.objects.all():
        report_context = report_data(start_time, end_time, team)
        report_charts = {
            "learner_goals_chart": charts.NewLearnersGoalsChart(start_time, end_time, report_context["new_applications"], team).generate(output="png")
        }
        # If there wasn't any activity during this period discard the update
        if report_context['active'] is False:
            continue
        report_context.update(context)
        report_context.update(report_charts)
        timezone.activate(pytz.timezone(settings.TIME_ZONE)) #TODO not sure what this influences anymore?
        translation.activate(settings.LANGUAGE_CODE)
        html_body = render_html_with_css('studygroups/email/weekly-update.html', report_context)
        text_body = render_to_string('studygroups/email/weekly-update.txt', report_context)
        timezone.deactivate()

        to = [o.user.email for o in team.teammembership_set.filter(role=TeamMembership.ORGANIZER)]
        update = EmailMultiAlternatives(
            _('Weekly learning circles update'),
            text_body,
            settings.DEFAULT_FROM_EMAIL,
            to
        )
        update.attach_alternative(html_body, 'text/html')
        update.send()

    # send weekly update to staff
    report_context = report_data(start_time, end_time)
    report_charts = {
        "learner_goals_chart": charts.NewLearnersGoalsChart(start_time, end_time, report_context["new_applications"]).generate(output="png")
    }
    report_context.update(context)
    report_context.update(report_charts)
    timezone.activate(pytz.timezone(settings.TIME_ZONE))
    translation.activate(settings.LANGUAGE_CODE)
    html_body = render_html_with_css('studygroups/email/weekly-update.html', report_context)
    text_body = render_to_string('studygroups/email/weekly-update.txt', report_context)
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
        "learner_goals_chart": charts.NewLearnerGoalsChart(end_date.date(), context['new_applications']).generate(output="png"),
        "top_topics_chart": charts.TopTopicsChart(end_date.date(), context['studygroups_that_met']).generate(output="png"),
    }

    context.update(chart_data)

    subject = render_to_string('studygroups/email/community_digest-subject.txt', context)
    html_body = render_html_with_css('studygroups/email/community_digest.html', context)
    text_body = html_body_to_text(html_body)
    to = [settings.COMMUNITY_DIGEST_EMAIL]

    msg = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, to)
    msg.attach_alternative(html_body, 'text/html')
    msg.send()


@shared_task
def send_reminders():
    """ Send meeting reminders """
    now = timezone.now()
    translation.activate(settings.LANGUAGE_CODE)
    # TODO - should this be set here or closer to where the language matters?
    # make sure both the StudyGroup and Meeting is still available
    reminders = Reminder.objects.filter(
        sent_at__isnull=True,
        study_group__in=StudyGroup.objects.published(),
        study_group_meeting__in=Meeting.objects.active()
    )
    for reminder in reminders:
        # don't send reminders older than the meeting
        meeting_datetime = reminder.study_group_meeting.meeting_datetime()
        if reminder.study_group_meeting and meeting_datetime - now < datetime.timedelta(days=2) and meeting_datetime > now:
            send_reminder(reminder)


@shared_task
def gen_reminders():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        generate_reminder(study_group)


@shared_task
def weekly_update():
    # Create a report for the previous week
    send_weekly_update()

@shared_task
def send_new_studygroup_emails():
    # send email to organizers who created a learning circle a week ago
    now = timezone.now()
    seven_days_ago = now.date() - datetime.timedelta(days=7)
    six_days_ago = now.date() - datetime.timedelta(days=6)
    for studygroup in StudyGroup.objects.filter(created_at__gte=seven_days_ago, created_at__lt=six_days_ago):
        send_new_studygroup_email(studygroup)


@shared_task
def send_all_studygroup_survey_reminders():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        send_learner_surveys(study_group)


@shared_task
def send_all_facilitator_surveys():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        send_facilitator_survey(study_group)


@shared_task
def send_all_last_week_group_activities():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        send_last_week_group_activity(study_group)

@shared_task
def send_all_facilitator_survey_reminders():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        send_facilitator_survey_reminder(study_group)

@shared_task
def send_all_learning_circle_reports():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        send_final_learning_circle_report(study_group)

@shared_task
def send_out_community_digest():
    translation.activate(settings.LANGUAGE_CODE)
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    iso_week = today.isocalendar()[1]
    end_date = today
    start_date = end_date - datetime.timedelta(days=21)

    if iso_week % 3 == 0:
        send_community_digest(start_date, end_date)
