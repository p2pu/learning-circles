from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView

from django.utils.decorators import method_decorator
from studygroups.decorators import user_is_group_facilitator

from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Course
from studygroups.models import Application
from studygroups.charts import LearnerGoalsChart, NewLearnersChart, CompletionRateChart, GoalsMetChart, SkillsLearnedChart



@method_decorator(user_is_group_facilitator, name='dispatch')
class StudyGroupFinalReport(TemplateView):
    template_name = 'studygroups/final_report.html'

    def get_context_data(self, **kwargs):
        context = super(StudyGroupFinalReport, self).get_context_data(**kwargs)
        study_group = get_object_or_404(StudyGroup, pk=kwargs.get('study_group_id'))
        learner_goals_chart = LearnerGoalsChart(study_group)
        new_learners_chart = NewLearnersChart(study_group)
        completion_rate_chart = CompletionRateChart(study_group)
        goals_met_chart = GoalsMetChart(study_group)
        skills_learned_chart = SkillsLearnedChart(study_group)

        context = {
            'study_group': study_group,
            'learner_goals_chart': learner_goals_chart.generate(),
            'new_learners_chart': new_learners_chart.generate(),
            'completion_rate_chart': completion_rate_chart.generate(),
            'goals_met_chart': goals_met_chart.generate(),
            'skills_learned_chart': skills_learned_chart.generate(),
        }

        return context
