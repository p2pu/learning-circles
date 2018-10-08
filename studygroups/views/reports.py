from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView

from django.utils.decorators import method_decorator
from studygroups.decorators import user_is_group_facilitator

from studygroups.models import StudyGroup
from studygroups.models import Meeting
from studygroups.models import Course
from studygroups.models import Application


@method_decorator(user_is_group_facilitator, name='dispatch')
class StudyGroupFinalReport(TemplateView):
    template_name = 'studygroups/final_report.html'

    def get_context_data(self, **kwargs):
        context = super(StudyGroupFinalReport, self).get_context_data(**kwargs)
        study_group = get_object_or_404(StudyGroup, pk=kwargs.get('study_group_id'))
        context['study_group_uuid'] = study_group.uuid

        return context
