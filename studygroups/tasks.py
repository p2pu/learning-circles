from celery import shared_task
from twilio.base.exceptions import TwilioRestException
from email.mime.text import MIMEText

from django.conf import settings
from django.utils import timezone
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse

from studygroups.models import StudyGroup, Meeting, Reminder, Team, TeamMembership
from studygroups.models import report_data
from studygroups.models import community_digest_data
from studygroups.models import get_study_group_organizers
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


logger = logging.getLogger(__name__)


def generate_reminder(study_group):
    now = timezone.now()
    next_meeting = study_group.next_meeting()
    # TODO reminder generation code should be moved to models, only sending facilitator notification should be here
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
            }
            previous_meeting = study_group.meeting_set.filter(meeting_date__lt=next_meeting.meeting_date).order_by('meeting_date').last()
            if previous_meeting and previous_meeting.feedback_set.first():
                context['feedback'] = previous_meeting.feedback_set.first()
            timezone.activate(pytz.timezone(study_group.timezone))
            with use_language(study_group.language):
                reminder.email_subject = render_to_string_ctx(
                    'studygroups/email/reminder-subject.txt',
                    context
                ).strip('\n')
                reminder.email_body = render_to_string_ctx(
                    'studygroups/email/reminder.txt',
                    context
                )
                reminder.sms_body = render_to_string_ctx(
                    'studygroups/email/sms.txt',
                    context
                )
            # TODO - handle SMS reminders that are too long
            if len(reminder.sms_body) > 160:
                logger.error('SMS body too long: ' + reminder.sms_body)
            reminder.sms_body = reminder.sms_body[:160]
            reminder.save()

            with use_language(reminder.study_group.language):
                facilitator_notification_subject = _('A reminder for %(course_title)s was generated' % {"course_title": study_group.course.title})
                facilitator_notification_html = render_html_with_css(
                    'studygroups/email/reminder_notification.html',
                    context
                )
                facilitator_notification_txt = render_to_string_ctx(
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


def _send_facilitator_survey(study_group):
    facilitator_name = study_group.facilitator.first_name
    path = reverse('studygroups_facilitator_survey', kwargs={'study_group_uuid': study_group.uuid})
    base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
    survey_url = base_url + path

    context = {
        'study_group': study_group,
        'facilitator': study_group.facilitator,
        'facilitator_name': facilitator_name,
        'survey_url': survey_url,
        'course_title': study_group.course.title,
    }

    timezone.deactivate()
    subject, txt, html = render_email_templates(
        'studygroups/email/facilitator_survey',
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


# If called directly, be sure to activate the current language
# Should be called every hour at :30
def send_facilitator_survey(study_group):
    """ send survey to all facilitators two days before their second to last meeting """
    last_meeting = study_group.meeting_set.active().order_by('-meeting_date', '-meeting_time').first()
    if not last_meeting:
        return
    now = timezone.now()
    start_of_window = now.replace(minute=0, second=0, microsecond=0)
    end_of_window = start_of_window + datetime.timedelta(hours=1)
    time_to_send = last_meeting.meeting_datetime() - datetime.timedelta(hours=1)

    if start_of_window <= time_to_send and time_to_send < end_of_window:
        _send_facilitator_survey(study_group)


# send prompt to facilitators to ask learners to complete surveys
# should be called every hour at :30
def send_facilitator_learner_survey_prompt(study_group):

    # TODO not supported for non-English learning circles
    if study_group.language != 'en':
        return

    now = timezone.now()

    # a learning circle could have no meetings and be published
    last_meeting = study_group.meeting_set.active().order_by('-meeting_date', '-meeting_time').first()
    if not last_meeting:
        logger.warning('Published learning circle does not have any associated meetings. StudyGroup.id={0}'.format(study_group.id))
        return

    start_of_window = now.replace(minute=0, second=0, microsecond=0)
    end_of_window = start_of_window + datetime.timedelta(hours=1)
    time_to_send = last_meeting.meeting_datetime() + datetime.timedelta(days=2)

    if start_of_window <= time_to_send and time_to_send < end_of_window:
        timezone.deactivate()

        facilitator_name = study_group.facilitator.first_name
        facilitator_survey_path = reverse(
            'studygroups_facilitator_survey',
            kwargs={'study_group_uuid': study_group.uuid}
        )
        learner_survey_path = reverse(
            'studygroups_learner_survey',
            kwargs={'study_group_uuid': study_group.uuid}
        )
        report_path = reverse('studygroups_final_report', kwargs={'study_group_id': study_group.id})
        base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
        facilitator_survey_url = base_url + facilitator_survey_path
        learner_survey_url = base_url + learner_survey_path
        report_url = base_url + report_path
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
            'studygroups/email/facilitator_learner_survey_prompt',
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
    # TODO not supported for non-English learning circles
    if study_group.language != 'en':
        return

    now = timezone.now()
    start_of_window = now.replace(minute=0, second=0, microsecond=0)
    end_of_window = start_of_window + datetime.timedelta(hours=1)

    last_meeting = study_group.meeting_set.active().order_by('-meeting_date', '-meeting_time').first()
    if not last_meeting:
        logger.warning('Published learning circle does not have any associated meetings. StudyGroup.id={0}'.format(study_group.id))
        return

    time_to_send = last_meeting.meeting_datetime() + datetime.timedelta(days=7)

    if start_of_window <= time_to_send and time_to_send < end_of_window:
        timezone.deactivate()

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
            'goals_met_chart': goals_met_chart.generate(output="png"),
        }

        subject = render_to_string_ctx('studygroups/email/learning_circle_final_report-subject.txt', context).strip('\n')
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


def send_learner_survey(application):
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
    facilitator_email = application.study_group.facilitator.email

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
        reply_to=[facilitator_email, settings.DEFAULT_FROM_EMAIL]
    )
    notification.attach_alternative(html, 'text/html')
    notification.send()


# send an hour before the last meeting
# should be called every hour at :30
def send_learner_surveys(study_group):
    if study_group.language != 'en':
        # TODO surveys only supported in English
        return

    last_meeting = study_group.meeting_set.active().order_by('-meeting_date', '-meeting_time').first()
    if not last_meeting:
        return

    time_to_send = last_meeting.meeting_datetime() - datetime.timedelta(hours=1)
    start_of_window = timezone.now().replace(minute=0, second=0, microsecond=0)
    end_of_window = start_of_window + datetime.timedelta(hours=1)

    if start_of_window <= time_to_send and time_to_send < end_of_window:
        applications = study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')
        timezone.deactivate()

        for application in applications:
            send_learner_survey(application)


def send_meeting_reminder(reminder):
    to = [su.email for su in reminder.study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')]
    sender = 'P2PU <{0}>'.format(settings.DEFAULT_FROM_EMAIL)

    for email in to:
        # activate correct language
        with use_language(reminder.study_group.language):
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
            "facilitator": reminder.study_group.facilitator
        }
        # activate learning circle language
        with use_language(reminder.study_group.language):
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


@shared_task
def send_meeting_change_notification(old_meeting, new_meeting):
    study_group = new_meeting.study_group
    to = [su.email for su in study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')]
    context = {
        'old_meeting': old_meeting,
        'new_meeting': new_meeting,
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
        report_context = report_data(start_time, end_time, team)
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
            cc=to
        )
        update.attach_alternative(html_body, 'text/html')
        update.send()

    # send weekly update to staff
    report_context = report_data(start_time, end_time)
    report_context.update(context)
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
    now = timezone.now()
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
def send_all_facilitator_survey_reminders():
    for study_group in StudyGroup.objects.published():
        translation.activate(settings.LANGUAGE_CODE)
        send_facilitator_learner_survey_prompt(study_group)


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
