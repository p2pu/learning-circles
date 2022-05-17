# coding=utf-8
from django.db import models
from django.db.models import Count, Max, Q, Sum, Case, When, IntegerField, Value, OuterRef, Subquery
from django.db.models import Window
from django.db.models import F
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse  # TODO ideally this shouldn't be in the model
from collections import Counter

from .base import SoftDeleteQuerySet
from .base import LifeTimeTrackingModel
from .course import Course
from .team import *
from .announcement import Announcement
from .profile import Profile
from .learningcircle import StudyGroup
from .learningcircle import Meeting
from .learningcircle import Application
from .learningcircle import Reminder
from .learningcircle import Rsvp
from .learningcircle import Feedback
from .facilitator_guide import FacilitatorGuide

import datetime
import pytz
import requests


def accept_application(application):
    # add a study group application to a study group
    application.accepted_at = timezone.now()
    application.save()


def application_mobile_opt_out(mobile):
    """ Opt-out user with given mobile number """
    applications = Application.objects.active().filter(
        mobile=mobile, mobile_opt_out_at__isnull=True
    )
    applications.update(mobile_opt_out_at=timezone.now())
    # TODO smarter handling for multiple applications


def application_mobile_opt_out_revert(mobile):
    """ Cancel opt-out for applications with given mobile number """
    applications = Application.objects.active().filter(
        mobile=mobile, mobile_opt_out_at__isnull=False
    )
    applications.update(mobile_opt_out_at=None)


def create_rsvp(contact, study_group, meeting_datetime, attending):
    # expect meeting_date as python datetime
    # contact is an email address of mobile number
    # study_group is the study group id
    study_group_meeting = Meeting.objects.active().get(study_group__id=study_group, meeting_date=meeting_datetime.date(), meeting_time=meeting_datetime.time())
    application = None
    if '@' in contact:
        application = Application.objects.active().get(study_group__id=study_group, email__iexact=contact)
    else:
        application = Application.objects.active().get(study_group__id=study_group, mobile=contact)
    rsvp = Rsvp.objects.all().filter(study_group_meeting=study_group_meeting, application=application).first()
    if not rsvp:
        rsvp = Rsvp(study_group_meeting=study_group_meeting, application=application, attending=attending=='yes')
    else:
        rsvp.attending = attending=='yes'
    rsvp.save()
    return rsvp


def generate_all_meetings(study_group):
    # TODO this should be deprecated
    # Something like create_weekly_meetings(sg, start, count) could replace this
    if Meeting.objects.active().filter(study_group=study_group).exists():
        raise Exception(_('Meetings already exist for this study group'))

    meeting_date = study_group.start_date
    meetings = []
    while meeting_date <= study_group.end_date:
        meeting = Meeting(
            study_group=study_group,
            meeting_date=meeting_date,
            meeting_time=study_group.meeting_time
        )
        #meeting.save()
        meetings += [meeting]
        meeting_date += datetime.timedelta(days=7)

    for meeting in meetings:
        meeting.save()


def generate_meetings_from_dates(study_group, meeting_dates=[]):
    existing_meetings = Meeting.objects.active().filter(study_group=study_group)
    meetings_to_keep = []

    for date in meeting_dates:
        meeting_date = date['meeting_date']
        meeting_time = date['meeting_time']

        this_meeting = existing_meetings.filter(meeting_date=meeting_date, meeting_time=meeting_time).first()
        if not this_meeting:
            this_meeting = Meeting(
                study_group=study_group,
                meeting_date=meeting_date,
                meeting_time=meeting_time
            )
            this_meeting.save()
        meetings_to_keep.append(this_meeting)

    for meeting in existing_meetings:
        if meeting not in meetings_to_keep:
            meeting.delete()


def generate_all_meeting_dates(start_date, meeting_time, weeks):
    """ generate a weekly meeting schedule """
    meeting_dates = []
    for i in range(weeks):
        meeting_dates += [{
            'meeting_date': start_date + datetime.timedelta(days=i*7),
            'meeting_time': meeting_time,
        }]
    return meeting_dates


def get_all_meeting_times(study_group):
    # sorted ascending according to date
    # times are in the study group timezone
    # meeting time stays constant, eg 18:00 stays 18:00 even when daylight savings changes
    tz = pytz.timezone(study_group.timezone)
    meeting_date = study_group.start_date
    meetings = []
    while meeting_date <= study_group.end_date:
        next_meeting = tz.localize(datetime.datetime.combine(meeting_date, study_group.meeting_time))
        meetings += [next_meeting]
        meeting_date += datetime.timedelta(days=7)
    return meetings


def report_data(today, team=None):
    """ Return data for the indicated time period

    If team is given, learning circles will be filtered by team

    past  last week start  this week start  now  this week ends
    <-----------|----------------|-----------|----------|------->
              Monday           Monday     Monday+     Monday
    """

    # dates
    # - to start -> in the future.
    # - meeting this week -> in the next 7 days
    # - wrapping up -> 7 days before
    # - feedback -> 7 days before
    # - signups -> past 7 days
    # - learning resources -> past 7 days
    # - facilitator guides -> past 7 days
    # todays date
    # start of this week

    week_start = today - datetime.timedelta(days=today.weekday())
    week_end = week_start + datetime.timedelta(days=7)
    last_week_start = week_start - datetime.timedelta(days=7)

    study_groups = StudyGroup.objects.published()

    # TODO should creation date or start date determine lc #
    _facilitator_groups = StudyGroup.objects.published().filter(
        facilitator=OuterRef('facilitator'),
        start_date__lte=OuterRef('start_date')
    ).order_by().values('facilitator').annotate(number=Count('pk'))

    upcoming_studygroups = StudyGroup.objects.published().annotate(
        lc_number=_facilitator_groups.values('number')[:1]
    ).filter(start_date__gte=week_start)

    studygroups_that_will_meet =  StudyGroup.objects.published().filter(meeting__meeting_date__gte=week_start, meeting__meeting_date__lt=week_end, meeting__deleted_at__isnull=True).distinct()

    meetings_this_week = Meeting.objects.active()\
        .filter(meeting_date__gte=week_start, meeting_date__lt=week_end)\
        .filter(study_group__in=study_groups)

    studygroups_that_ended = study_groups.filter(end_date__gte=last_week_start, end_date__lt=week_start)

    feedback = Feedback.objects.filter(study_group_meeting__meeting_date__gte=last_week_start, study_group_meeting__meeting_date__lt=week_start)

    new_applications = Application.objects.active().filter(created_at__gte=last_week_start, created_at__lt=week_start)

    new_users = User.objects.filter(date_joined__gte=last_week_start, date_joined__lt=week_start)

    new_courses = Course.objects.active().filter(created_at__gte=last_week_start, created_at__lt=week_start, unlisted=False)

    new_facilitator_guides = FacilitatorGuide.objects.active().filter(created_at__gte=last_week_start)


    if team:
        members = team.teammembership_set.active().values_list('user', flat=True)
        new_courses = new_courses.filter(created_by__in=members)
        new_applications = new_applications.filter(study_group__team=team)
        meetings_this_week = meetings_this_week.filter(study_group__team=team)
        study_groups = study_groups.filter(team=team)
        feedback = feedback.filter(study_group_meeting__study_group__team=team)

        studygroups_that_ended = studygroups_that_ended.filter(team=team)
        studygroups_that_will_meet = studygroups_that_will_meet.filter(team=team)
        new_members = team.teammembership_set.active().filter(created_at__gte=last_week_start, created_at__lt=week_start).values('user')
        new_users = User.objects.filter(id__in=new_members)
        upcoming_studygroups = upcoming_studygroups.filter(team=team)

    learners_reached = Application.objects.active().filter(study_group__in=studygroups_that_will_meet)
    studygroups_with_survey_responses = filter_studygroups_with_survey_responses(studygroups_that_ended)

    active = any([
        upcoming_studygroups.count() > 0,
        meetings_this_week.count() > 0,
        studygroups_that_ended.count() > 0,
        feedback.count() > 0,
        new_applications.count() > 0,
        new_users.count() > 0,
        new_courses.count() > 0,
    ])

    report = {
        'start_time': week_start,
        'active': active,
        'meetings': meetings_this_week,
        'feedback': feedback,
        "finished_studygroups": studygroups_that_ended,
        "finished_studygroups_count": studygroups_that_ended.count(),
        "studygroups_met_count": studygroups_that_will_meet.count(), # TODO rename context var
        "learners_reached_count": learners_reached.count(),
        "upcoming_studygroups": upcoming_studygroups,
        "upcoming_studygroups_count": upcoming_studygroups.count(),
        "new_applications": new_applications,
        "new_learners_count": new_applications.count(),
        "new_users": new_users,
        "new_users_count": new_users.count(),
        "new_courses": new_courses,
        "new_courses_count": new_courses.count(),
        "new_facilitator_guides": new_facilitator_guides,
    }

    if team:
        report['team'] = team
    return report

def get_json_response(url):
    response = requests.get(url)
    try:
        return response.json()
    except:
        raise ConnectionError("Request to {} returned {}".format(url, response.status_code))


def get_studygroups_with_meetings(start_time, end_time, team=None):
    if team:
        return StudyGroup.objects.published().filter(team=team, meeting__meeting_date__gte=start_time, meeting__meeting_date__lt=end_time, meeting__deleted_at__isnull=True).distinct()

    return StudyGroup.objects.published().filter(meeting__meeting_date__gte=start_time, meeting__meeting_date__lt=end_time, meeting__deleted_at__isnull=True).distinct()

def get_new_studygroups(start_time, end_time):
    return StudyGroup.objects.published().filter(created_at__gte=start_time, created_at__lt=end_time)

def get_new_users(start_time, end_time, team=None):
    if team:
        new_user_ids = team.teammembership_set.active().filter(created_at__gte=start_time, created_at__lt=end_time).values('user')
        return User.objects.filter(id__in=new_user_ids)

    return User.objects.filter(date_joined__gte=start_time, date_joined__lt=end_time)

def get_new_applications(start_time, end_time):
    return Application.objects.active().filter(created_at__gte=start_time, created_at__lt=end_time)

def get_new_courses(start_time, end_time):
    return Course.objects.active().filter(created_at__gte=start_time, created_at__lt=end_time, unlisted=False)

def get_upcoming_studygroups(start_time):
    end_time = start_time + datetime.timedelta(days=21)
    return StudyGroup.objects.published().filter(start_date__gte=start_time, start_date__lt=end_time)

def get_studygroups_that_ended(start_time, end_time, team=None):
    if team:
        return StudyGroup.objects.published().filter(end_date__gte=start_time, end_date__lt=end_time, team=team)
    return StudyGroup.objects.published().filter(end_date__gte=start_time, end_date__lt=end_time)

def filter_studygroups_with_survey_responses(study_groups):
    with_responses = filter(lambda sg: sg.learnersurveyresponse_set.count() > 0, study_groups)
    return sorted(with_responses, key=lambda sg: sg.learnersurveyresponse_set.count(), reverse=True)

def get_new_user_intros(new_users, limit=5):
    new_discourse_users = [ '{} {}'.format(user.first_name, user.last_name) for user in new_users ]

    # TODO if this request fails, the whole weekly update will fail
    latest_introduction_posts = get_json_response("https://community.p2pu.org/t/1571/last.json")

    intros_from_new_users = []
    for post in latest_introduction_posts['post_stream']['posts']:

        discourse_user = post.get("name", None)

        if settings.DEBUG and discourse_user is not None:
            discourse_user = discourse_user.split(" ")[0] + " Lastname" # TODO remove this on production!!

        if discourse_user in new_discourse_users and post["reply_to_post_number"] is None:
            intros_from_new_users.append(post)

    return intros_from_new_users[::-1][:limit]

def get_discourse_categories():
    site_json = get_json_response("https://community.p2pu.org/site.json")
    return site_json['categories']

def get_top_discourse_topics_and_users(limit=10):
    top_posts_json = get_json_response("https://community.p2pu.org/top/monthly.json")
    return { 'topics': top_posts_json['topic_list']['topics'][:limit], 'users': top_posts_json['users'] }

def get_active_teams():
    today = datetime.datetime.now()
    two_weeks_ago = today - relativedelta(days=+14)
    memberships = StudyGroup.objects.published().filter(Q(start_date__gte=today) | Q(start_date__lte=today, end_date__gte=today) | Q(end_date__gt=two_weeks_ago, end_date__lte=today)).values_list('facilitator__teammembership', flat=True)
    active_teams = Team.objects.filter(teammembership__in=memberships).distinct()
    return active_teams

def get_active_facilitators():
    # TODO studygroup_count will include any deleted or draft studygroups once
    # iow, actual count might be off by 1, but total won't be over inflated
    facilitators = User.objects.annotate(\
        studygroup_count=Count(
            Case(
                When(
                    studygroup__draft=False, studygroup__deleted_at__isnull=True,
                    then=F('studygroup__id')
                ),
                default=Value(0),
                output_field=IntegerField()
            ),
            distinct=True
        ),
        latest_end_date=Max(
            Case(
                When(
                    studygroup__draft=False,
                    studygroup__deleted_at__isnull=True,
                    then='studygroup__end_date'
                )
            )
        ),
        learners_count=Sum(
            Case(
                When(
                    studygroup__draft=False,
                    studygroup__deleted_at__isnull=True,
                    studygroup__application__deleted_at__isnull=True,
                    studygroup__application__accepted_at__isnull=False, then=1
                ),
                output_field=IntegerField()
            )
        )
    ).filter(studygroup_count__gte=2).order_by('-studygroup_count')

    return facilitators

def get_unrated_studygroups():
    today = datetime.datetime.now()
    two_months_ago = today - relativedelta(months=+2)
    unrated_studygroups = StudyGroup.objects.published()\
        .annotate(
            application__count = models.Count('application', filter=
                Q(application__deleted_at__isnull=True, application__accepted_at__isnull=False))
        )\
        .annotate( facilitatorsurveyresponse__count = models.Count('facilitatorsurveyresponse') )\
        .filter(
            application__count__gte=1,
            end_date__gte=two_months_ago,
            end_date__lt=today
        ).filter(
            facilitator_rating__isnull=True,
            facilitator_goal_rating__isnull=True,
            facilitatorsurveyresponse__count=0
        ).order_by('-end_date')
    return unrated_studygroups

def get_unpublished_studygroups(start_time, end_time):
    return StudyGroup.objects.filter(draft=True, created_at__lt=end_time, created_at__gte=start_time).order_by('created_at')

def get_studygroups_meetings(start_time, end_time):
    return Meeting.objects.active().filter(meeting_date__gte=start_time, meeting_date__lt=end_time, study_group__deleted_at__isnull=True, study_group__draft=False)

def community_digest_data(start_time, end_time):
    origin_date = datetime.date(2016, 1, 1)

    studygroups_that_met = get_studygroups_with_meetings(start_time, end_time)
    learners_reached = Application.objects.active().filter(study_group__in=studygroups_that_met)
    total_learners_reached_count = Application.objects.active().filter(accepted_at__gte=origin_date, accepted_at__lt=end_time).count()
    total_meetings_count = get_studygroups_meetings(origin_date, end_time).count()
    studygroups_meetings_count = get_studygroups_meetings(start_time, end_time).count()
    new_users = get_new_users(start_time, end_time)
    new_applications = get_new_applications(start_time, end_time)
    new_courses = get_new_courses(start_time, end_time)
    upcoming_studygroups = get_upcoming_studygroups(end_time)
    studygroups_that_ended = get_studygroups_that_ended(start_time, end_time)
    studygroups_with_survey_responses = filter_studygroups_with_survey_responses(studygroups_that_ended)
    intros_from_new_users = get_new_user_intros(new_users)
    discourse_categories = get_discourse_categories()
    top_discourse_topics = get_top_discourse_topics_and_users()
    web_version_path = reverse('studygroups_community_digest', kwargs={'start_date': start_time.strftime("%d-%m-%Y"), 'end_date': end_time.strftime("%d-%m-%Y")})

    return {
        "start_date": start_time.date(),
        "end_date": end_time.date(),
        "studygroups_that_met": studygroups_that_met,
        "studygroups_meetings_count": studygroups_meetings_count,
        "learners_reached_count": learners_reached.count(),
        "new_users_count": new_users.count(),
        "upcoming_studygroups": upcoming_studygroups,
        "upcoming_studygroups_count": upcoming_studygroups.count(),
        "finished_studygroups": studygroups_that_ended,
        "finished_studygroups_count": len(studygroups_that_ended),
        "studygroups_with_survey_responses": studygroups_with_survey_responses,
        "new_applications": new_applications,
        "new_learners_count": new_applications.count(),  # TODO remove and use new_applications | length in templates
        "new_courses": new_courses,
        "new_courses_count": new_courses.count(),  # TODO remove and use `| length` in templates
        "top_discourse_topics": top_discourse_topics,
        "discourse_categories": discourse_categories,
        "intros_from_new_users": intros_from_new_users,
        "web_version_path": web_version_path,
        "total_learners_reached_count": total_learners_reached_count,
        "total_meetings_count": total_meetings_count,
    }


def stats_dash_data(start_time, end_time, team=None):
    studygroups_that_ended = get_studygroups_that_ended(start_time, end_time, team)
    studygroups_that_met = get_studygroups_with_meetings(start_time, end_time, team)
    unpublished_studygroups = get_unpublished_studygroups(start_time, end_time)
    learners_reached = Application.objects.active().filter(study_group__in=studygroups_that_met)
    courses = studygroups_that_met.values_list('course', 'course__title')
    ordered_courses = Counter(courses).most_common(10)
    top_courses = [{ "title": course[0][1], "course_id": course[0][0], "count": course[1] } for course in ordered_courses]
    active_teams = get_active_teams()
    active_facilitators = get_active_facilitators()
    unrated_studygroups = get_unrated_studygroups()

    return {
        "start_date": start_time.date(),
        "end_date": end_time.date(),
        "studygroups_that_met": studygroups_that_met,
        "studygroups_that_ended": studygroups_that_ended,
        "studygroups_met_count": studygroups_that_met.count(),
        "learners_reached_count": learners_reached.count(),
        "top_courses": top_courses,
        "active_teams": active_teams,
        "active_facilitators": active_facilitators,
        "unrated_studygroups": unrated_studygroups,
        "unpublished_studygroups": unpublished_studygroups,
    }
