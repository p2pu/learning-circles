from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.conf import settings

from django.utils.decorators import method_decorator
from studygroups.decorators import user_is_staff

from studygroups.models import StudyGroup
from studygroups.models import Team
from studygroups.models import community_digest_data
from studygroups.models import stats_dash_data
from studygroups import charts

from surveys.models import FacilitatorSurveyResponse

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware

import requests


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

        digest_data = community_digest_data(start_date, end_date)

        chart_data = {
            "meetings_chart": charts.LearningCircleMeetingsChart(end_date.date()).generate(), # why does the svg set text-anchor: middle on the x_labels?!?!
            "countries_chart": charts.LearningCircleCountriesChart(start_date.date(), end_date.date()).generate(),
            "learner_goals_chart": charts.NewLearnerGoalsChart(end_date.date(), digest_data['new_applications']).generate(),
            "top_topics_chart": charts.TopTopicsChart(end_date.date(), digest_data['studygroups_that_met']).generate(),
        }

        context.update(digest_data)
        context.update(chart_data)
        context.update({ "web": True })

        return context

def get_low_rated_courses():
    survey_responses = FacilitatorSurveyResponse.objects.all()

    low_rated_courses = []

    for response in survey_responses:
        field = charts.get_response_field(response.response, "Zm9XlzKGKC66")
        # Zm9XlzKGKC66 = "How well did the online course {{hidden:course}} work as a learning circle?"
        if field is not None and field['number'] < 3:
            if response.study_group.course.unlisted is False:
                low_rated_courses.append((response.study_group.course, field['number']))

    return low_rated_courses


@method_decorator(user_is_staff, name='dispatch')
class StatsDashView(TemplateView):
    template_name = 'studygroups/stats_dash.html'

    def get_context_data(self, **kwargs):
        context = super(StatsDashView, self).get_context_data(**kwargs)
        start_time = make_aware(datetime.strptime(kwargs.get('start_date'), "%m-%Y"))
        end_time = make_aware(datetime.strptime(kwargs.get('end_date'), "%m-%Y")) + relativedelta(day=31)
        minimum_start_time = end_time - relativedelta(months=+2, day=1)
        start_time = minimum_start_time if start_time > minimum_start_time else start_time

        team_id = kwargs.get('team_id', None)
        team = Team.objects.filter(pk=team_id).first()

        data = stats_dash_data(start_time, end_time, team)

        # this doesn't belong here
        # it should be in stats_dash_data
        # but importing surveys.models into studygroups.models creates a circular dependency :(
        low_rated_courses = get_low_rated_courses()

        chart_data = {
            "meetings_over_time_chart": charts.MeetingsOverTimeChart(start_time, end_time).generate(),
            "facilitator_rating_percentage_chart" : charts.FacilitatorRatingOverTimeChart(start_time, end_time, data["studygroups_that_ended"]).generate(),
            "studygroups_by_country_chart": charts.StudygroupsByCountryOverTimeChart(start_time, end_time, data["studygroups_that_ended"]).generate(),
            "facilitator_course_approval_chart" : charts.FacilitatorCourseApprovalChart(start_time, end_time, data["studygroups_that_ended"]).generate(),
            "learner_course_approval_chart" : charts.LearnerCourseApprovalChart(start_time, end_time, data["studygroups_that_ended"]).generate(),
            # "learner_course_rating_percentage_chart" : charts.LearnerCourseRatingPercentageChart(start_time, end_time, data["studygroups_that_ended"]).generate(),
            "facilitator_experience_chart" : charts.FacilitatorExperienceChart(start_time, end_time, data["studygroups_that_met"]).generate(),
            # "top_facilitators_chart" : charts.TopFacilitatorsChart(start_time, end_time, data["studygroups_that_met"]).generate(),
            "participants_over_time_chart" : charts.ParticipantsOverTimeChart(start_time, end_time, data["studygroups_that_met"]).generate(),
            "learner_goal_reached_chart" : charts.LearnerGoalReachedChart(start_time, end_time, data["studygroups_that_ended"]).generate(),
            "skills_improved_chart" : charts.SkillsImprovedChart(start_time, end_time, data["studygroups_that_ended"]).generate(),
            # "top_courses_chart" : charts.TopCoursesChart(start_time, end_time, data["studygroups_that_met"]).generate(),
        }

        context.update(data)
        context.update({ "low_rated_courses": low_rated_courses })
        context.update(chart_data)


        if team:
            context.update({ "team": team })

        return context

