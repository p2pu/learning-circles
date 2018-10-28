from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings

from django.utils.decorators import method_decorator
from studygroups.decorators import user_is_group_facilitator

from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import Course
from studygroups import charts

from datetime import datetime, timedelta
from django.utils.timezone import make_aware

import requests


def get_json_response(url):
    response = requests.get(url)
    return response.json()

def get_studygroups_with_meetings(start_time, end_time):
    return StudyGroup.objects.published().filter(meeting__meeting_date__gte=start_time, meeting__meeting_date__lt=end_time, meeting__deleted_at__isnull=True).distinct()

def get_new_studygroups(start_time, end_time):
    return StudyGroup.objects.published().filter(created_at__gte=start_time, created_at__lt=end_time)

def get_new_users(start_time, end_time):
    return User.objects.filter(date_joined__gte=start_time, date_joined__lt=end_time)

def get_new_applications(start_time, end_time):
    return Application.objects.active().filter(created_at__gte=start_time, created_at__lt=end_time)

def get_new_courses(start_time, end_time):
    return Course.objects.active().filter(created_at__gte=start_time, created_at__lt=end_time, unlisted=False)

def get_upcoming_studygroups(start_time):
    end_time = start_time + timedelta(days=21)
    return StudyGroup.objects.filter(start_date__gte=start_time, start_date__lt=end_time)

def get_finished_studygroups(start_time, end_time):
    study_groups = StudyGroup.objects.published()
    finished_studygroups = []
    for sg in study_groups:
        last_meeting = sg.last_meeting()
        if last_meeting and last_meeting.meeting_datetime() > start_time and last_meeting.meeting_datetime() < end_time:
            finished_studygroups.append(last_meeting.study_group)

    return finished_studygroups

def filter_studygroups_with_survey_responses(study_groups):
    with_responses = filter(lambda sg: sg.learnersurveyresponse_set.count() > 0, study_groups)
    return sorted(with_responses, key=lambda sg: sg.learnersurveyresponse_set.count(), reverse=True)

def get_new_user_intros(new_users, limit=5):
    new_discourse_usernames = [ '{}_{}'.format(user.first_name, user.last_name) for user in new_users ]
    latest_introduction_posts = get_json_response("https://community.p2pu.org/t/1571/last.json")

    intros_from_new_users = []
    for post in latest_introduction_posts['post_stream']['posts']:
        discourse_username = post["username"]

        if settings.DEBUG:
            discourse_username = discourse_username.split("_")[0] + "_Lastname" # TODO remove this on production!!

        if discourse_username in new_discourse_usernames:
            intros_from_new_users.append(post)

    return intros_from_new_users[::-1][:limit]

def get_discourse_categories():
    site_json = get_json_response("https://community.p2pu.org/site.json")
    return site_json['categories']

def get_top_discourse_topics_and_users(limit=10):
    top_posts_json = get_json_response("https://community.p2pu.org/top/monthly.json")

    return { 'topics': top_posts_json['topic_list']['topics'][:limit], 'users': top_posts_json['users'] }

def get_data_for_community_digest(start_time, end_time, web=False):
    study_groups = StudyGroup.objects.published()

    studygroups_that_met = get_studygroups_with_meetings(start_time, end_time)
    learners_reached = Application.objects.active().filter(study_group__in=studygroups_that_met)
    new_learning_circles = get_new_studygroups(start_time, end_time)
    new_users = get_new_users(start_time, end_time)
    new_applications = get_new_applications(start_time, end_time)
    new_courses = get_new_courses(start_time, end_time)
    upcoming_studygroups = get_upcoming_studygroups(end_time)
    studygroups_that_ended = get_finished_studygroups(start_time, end_time)
    studygroups_with_survey_responses = filter_studygroups_with_survey_responses(studygroups_that_ended)
    intros_from_new_users = get_new_user_intros(new_users)
    discourse_categories = get_discourse_categories()
    top_discourse_topics = get_top_discourse_topics_and_users()
    graph_output = None if web else "png"
    web_version_path = reverse('studygroups_community_digest', kwargs={'start_date': start_time.strftime("%d-%m-%Y"), 'end_date': end_time.strftime("%d-%m-%Y")})
    web_version_url = settings.DOMAIN + web_version_path


    return {
        "start_date": start_time.date(),
        "end_date": end_time.date(),
        "studygroups_met_count": studygroups_that_met.count(),
        "learners_reached_count": learners_reached.count(),
        "new_users_count": new_users.count(),
        "upcoming_studygroups": upcoming_studygroups,
        "upcoming_studygroups_count": upcoming_studygroups.count(),
        "finished_studygroups": studygroups_that_ended,
        "finished_studygroups_count": len(studygroups_that_ended),
        "studygroups_with_survey_responses": studygroups_with_survey_responses,
        "new_learners_count": new_applications.count(),
        "new_courses": new_courses,
        "new_courses_count": new_courses.count(),
        "meetings_chart": charts.LearningCircleMeetingsChart(end_time.date(), Meeting).generate(output="png"), # why does the svg set text-anchor: middle on the x_labels?!?!
        "countries_chart": charts.LearningCircleCountriesChart(end_time.date(), StudyGroup).generate(output=graph_output),
        "learner_goals_chart": charts.NewLearnerGoalsChart(end_time.date(), new_applications).generate(output=graph_output),
        "top_topics_chart": charts.TopTopicsChart(end_time.date(), studygroups_that_met, StudyGroup, Course).generate(output=graph_output),
        "top_discourse_topics": top_discourse_topics,
        "discourse_categories": discourse_categories,
        "intros_from_new_users": intros_from_new_users,
        "web_version_url": web_version_url,
    }



class StudyGroupFinalReport(TemplateView):
    template_name = 'studygroups/final_report.html'

    def get_context_data(self, **kwargs):
        context = super(StudyGroupFinalReport, self).get_context_data(**kwargs)
        study_group = get_object_or_404(StudyGroup, pk=kwargs.get('study_group_id'))

        if study_group.learnersurveyresponse_set.count() == 0:
            context = {
                'study_group': study_group,
                'registrations': study_group.application_set.active().count(),
                'survey_responses': study_group.learnersurveyresponse_set.count()
            }

            return context

        learner_goals_chart = charts.LearnerGoalsChart(study_group)
        new_learners_chart = charts.NewLearnersChart(study_group)
        completion_rate_chart = charts.CompletionRateChart(study_group)
        goals_met_chart = charts.GoalsMetChart(study_group)
        skills_learned_chart = charts.SkillsLearnedChart(study_group)
        reasons_for_success_chart = charts.ReasonsForSuccessChart(study_group)
        next_steps_chart = charts.NextStepsChart(study_group)
        ideas_chart = charts.IdeasChart(study_group)
        facilitator_rating_chart = charts.FacilitatorRatingChart(study_group)
        learner_rating_chart = charts.LearnerRatingChart(study_group)
        promotion_chart = charts.PromotionChart(study_group)
        library_usage_chart = charts.LibraryUsageChart(study_group)
        additional_resources_chart = charts.AdditionalResourcesChart(study_group)
        facilitator_new_skills_chart = charts.FacilitatorNewSkillsChart(study_group)
        facilitator_tips_chart = charts.FacilitatorTipsChart(study_group)

        context = {
            'study_group': study_group,
            'registrations': study_group.application_set.active().count(),
            'survey_responses': study_group.learnersurveyresponse_set.count(),
            'course': study_group.course,
            'learner_goals_chart': learner_goals_chart.generate(),
            'goals_met_chart': goals_met_chart.generate(),
            'new_learners_chart': new_learners_chart.generate(),
            'completion_rate_chart': completion_rate_chart.generate(),
            'skills_learned_chart': skills_learned_chart.generate(),
            'reasons_for_success_chart': reasons_for_success_chart.generate(),
            'next_steps_chart': next_steps_chart.generate(),
            'ideas_chart': ideas_chart.generate(),
            'facilitator_rating_chart': facilitator_rating_chart.generate(),
            'learner_rating_chart': learner_rating_chart.generate(),
            'promotion_chart': promotion_chart.generate(),
            'library_usage_chart': library_usage_chart.generate(),
            'additional_resources_chart': additional_resources_chart.generate(),
            'facilitator_new_skills_chart': facilitator_new_skills_chart.generate(),
            'facilitator_tips_chart': facilitator_tips_chart.generate(),
        }

        return context


class CommunityDigestView(TemplateView):
    template_name = 'studygroups/community_digest.html'

    def get_context_data(self, **kwargs):
        context = super(CommunityDigestView, self).get_context_data(**kwargs)
        start_date = make_aware(datetime.strptime(kwargs.get('start_date'), "%d-%m-%Y"))
        end_date = make_aware(datetime.strptime(kwargs.get('end_date'), "%d-%m-%Y"))

        digest_data = get_data_for_community_digest(start_date, end_date, web=True)
        context.update(digest_data)
        context.update({ "web": True })

        return context

