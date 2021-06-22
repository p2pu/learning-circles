from django.core.management.base import BaseCommand, CommandError

from studygroups.models import StudyGroup
from surveys.models import FacilitatorSurveyResponse
from surveys.models import facilitator_survey_summary

class Command(BaseCommand):
    help = 'Transfer course ratings'

    def handle(self, *args, **options):
        for response in FacilitatorSurveyResponse.objects.all():
            study_group = response.study_group
            if not study_group:
                continue
            summary = facilitator_survey_summary(response)
            course_rating = summary.get('course_rating')
            if course_rating:
                study_group.course_rating = course_rating
            course_rating_reason = summary.get('course_rating_reason')
            if course_rating_reason:
                study_group.course_rating_reason = course_rating_reason
            study_group.save()
