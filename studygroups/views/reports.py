from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
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
from surveys.models import facilitator_survey_summary

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware

from studygroups.forms import StatsDashForm
from django.urls import reverse_lazy

import requests

import logging

logger = logging.getLogger(__name__)


class StudyGroupFinalReport(TemplateView):
    template_name = 'studygroups/final_report.html'

    def get_context_data(self, **kwargs):
        context = super(StudyGroupFinalReport, self).get_context_data(**kwargs)
        study_group = get_object_or_404(StudyGroup, pk=kwargs.get('study_group_id'))
        learner_survey_responses = study_group.learnersurveyresponse_set.count()
        facilitator_survey_responses = study_group.facilitatorsurveyresponse_set.count()

        if learner_survey_responses == 0 and facilitator_survey_responses == 0:
            context = {
                'study_group': study_group,
                'registrations': study_group.application_set.active().count(),
                'learner_survey_responses': learner_survey_responses,
                'facilitator_survey_responses': facilitator_survey_responses,
            }

            return context

        completion_rate_chart = charts.CompletionRateChart(study_group)
        goals_met_chart = charts.GoalsMetChart(study_group)

        context = {
            'study_group': study_group,
            'course': study_group.course,
            'registrations': study_group.application_set.active().count(),
            'learner_survey_responses': study_group.learnersurveyresponse_set.count(),
            'facilitator_survey_responses': study_group.facilitatorsurveyresponse_set.count(),
            'goals_chart': charts.goals_chart(study_group),
            'goals_met_chart': goals_met_chart.generate(),
            'topic_confidence_chart': charts.topic_confidence_chart(study_group),
            'next_steps_chart': charts.next_steps_chart(study_group),
            'completion_rate_chart': completion_rate_chart.generate(),
            'attendance_chart': charts.attendance_chart(study_group),
            'recommendation_chart': charts.recommendation_chart(study_group),
            'recommendation_reasons_chart': charts.recommendation_reasons_chart(study_group),
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
            "top_topics_chart": charts.TopTopicsChart(end_date.date(), digest_data['studygroups_that_met']).generate(),
        }

        context.update(digest_data)
        context.update(chart_data)
        context.update({ "web": True })

        return context


def get_low_rated_courses():
    survey_responses = FacilitatorSurveyResponse.objects.filter(study_group__isnull=False, study_group__course__unlisted=False)
    
    survey_responses = [(r.study_group.course, facilitator_survey_summary(r)) for r in survey_responses]
    low_rated_courses = [(c, r.get('course_rating')) for c, r in survey_responses if r.get('course_rating', 99) < 3 ]
    return low_rated_courses


@method_decorator(user_is_staff, name='dispatch')
class StatsDashView(FormView):
    template_name = 'studygroups/stats_dash.html'
    form_class = StatsDashForm
    success_url = reverse_lazy('studygroups_staff_dash_stats')

    def form_valid(self, form):
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        base_url = reverse_lazy('studygroups_staff_dash_stats')
        self.success_url = "{}?start_date={}&end_date={}".format(base_url, start_date, end_date)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(StatsDashView, self).get_context_data(**kwargs)
        start_date = self.request.GET.get('start_date', None)
        end_date = self.request.GET.get('end_date', None)
        today = datetime.now()
        end_time = make_aware(datetime.strptime(end_date, "%Y-%m-%d")) + relativedelta(day=31) if end_date else today
        start_time = make_aware(datetime.strptime(start_date, "%Y-%m-%d")) + relativedelta(day=1) if start_date else end_time - relativedelta(months=+3, day=1)

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
            "facilitator_experience_chart" : charts.FacilitatorExperienceChart(start_time, end_time, data["studygroups_that_met"]).generate(),
            "participants_over_time_chart" : charts.ParticipantsOverTimeChart(start_time, end_time, data["studygroups_that_met"]).generate(),
            "learner_goal_reached_chart" : charts.LearnerGoalReachedChart(start_time, end_time, data["studygroups_that_ended"]).generate(),
            "learner_response_rate_chart" : charts.LearnerResponseRateChart(start_time, end_time, data["studygroups_that_ended"]).generate(),
        }

        context.update(data)
        context.update({ "low_rated_courses": low_rated_courses })
        context.update(chart_data)


        if team:
            context.update({ "team": team })

        return context

