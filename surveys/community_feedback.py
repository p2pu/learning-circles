from django.core.serializers.json import DjangoJSONEncoder

from .models import FacilitatorSurveyResponse
from .models import LearnerSurveyResponse

from studygroups.models import StudyGroup
from .models import learner_survey_summary
from .models import facilitator_survey_summary

import json

def calculate_course_ratings(course):
    studygroup_ids = StudyGroup.objects.filter(course=course.id).distinct().values_list("id", flat=True)
    learner_surveys = LearnerSurveyResponse.objects.filter(study_group__in=studygroup_ids)
    facilitator_surveys = FacilitatorSurveyResponse.objects.filter(study_group__in=studygroup_ids)

    all_surveys = list(map(learner_survey_summary, learner_surveys))
    all_surveys += list(map(facilitator_survey_summary, facilitator_surveys))
    ratings = [s.get('course_rating') for s in all_surveys if s.get('course_rating')]

    step_counts = { i: sum(1 for x in ratings if x == i) for i in range(1,6) }
    ratings_sum = sum(ratings)
    total_ratings = len(ratings)
    overall_rating = round(ratings_sum / total_ratings, 2) if total_ratings > 0 else 0

    course.rating_step_counts = json.dumps(step_counts)
    course.overall_rating = overall_rating
    course.total_ratings = total_ratings
    course.learner_ratings = 10
    course.save()
