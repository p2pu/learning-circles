from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView

from django.utils.decorators import method_decorator
from studygroups.decorators import user_is_group_facilitator

from studygroups.models import StudyGroup
from studygroups import charts


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
