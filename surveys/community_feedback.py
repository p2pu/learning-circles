from django.core.serializers.json import DjangoJSONEncoder

from .models import FacilitatorSurveyResponse
from .models import LearnerSurveyResponse
from .models import MAX_STAR_RATING

from studygroups.models import StudyGroup

import json

def calculate_course_ratings(course):
    step_counts = {
        5: 0,
        4: 0,
        3: 0,
        2: 0,
        1: 0,
    }

    ratings_sum = 0
    total_ratings = 0

    studygroup_ids = StudyGroup.objects.filter(course=course.id).distinct().values_list("id", flat=True)
    learner_surveys = LearnerSurveyResponse.objects.filter(study_group__in=studygroup_ids)
    facilitator_surveys = FacilitatorSurveyResponse.objects.filter(study_group__in=studygroup_ids)

    for survey in learner_surveys:
        rating_question = survey.get_survey_field("iGWRNCyniE7s")
        rating_answer = survey.get_response_field("iGWRNCyniE7s")
        # iGWRNCyniE7s = "How well did the online course {{hidden:course}} work as a learning circle?"
        if rating_answer and 'number' in rating_answer:
            step_counts[rating_answer['number']] += 1
            ratings_sum += rating_answer['number']
            total_ratings += 1

    for survey in facilitator_surveys:
        rating_question = survey.get_survey_field("Zm9XlzKGKC66")
        rating_answer = survey.get_response_field("Zm9XlzKGKC66")

        # Zm9XlzKGKC66 = "How well did the online course {{hidden:course}} work as a learning circle?"
        if not rating_answer or 'number' not in rating_answer:
            # we can continue with this survey if we don't have a rating answer
            continue

        facilitator_rating = rating_answer['number']

        if rating_question and 'properties' in rating_question:
            facilitator_steps = rating_question['properties']['steps']

            # Normalize the rating if it doesn't match MAX_STAR_RATING
            if facilitator_steps != MAX_STAR_RATING:
                facilitator_rating = round(facilitator_rating/facilitator_steps * MAX_STAR_RATING)
        elif facilitator_rating > MAX_STAR_RATING:
            # if we don't know how many steps the rating has and it exceeds MAX_STAR_RATING
            # ignore this rating
            continue

        step_counts[facilitator_rating] += 1
        ratings_sum += facilitator_rating
        total_ratings += 1

    overall_rating = round(ratings_sum / total_ratings, 2) if total_ratings > 0 else 0
    rating_step_counts_json = json.dumps(step_counts, cls=DjangoJSONEncoder)

    course.total_ratings=total_ratings
    course.rating_step_counts=rating_step_counts_json
    course.overall_rating=overall_rating
    course.save()


def calculate_course_tagdorsements(course):
    tag_counts = {
        'Easy to use': 0,
        'Good for first time facilitators': 0,
        'Great for beginners': 0,
        'Engaging material': 0,
        'Led to great discussions': 0,
    }

    total_reviewers = 0

    studygroup_ids = StudyGroup.objects.filter(course=course.id).distinct().values_list("id", flat=True)
    facilitator_surveys = FacilitatorSurveyResponse.objects.filter(study_group__in=studygroup_ids)

    for survey in facilitator_surveys:
        response = survey.get_response_field("cNH3Ck0SHspB")
        # cNH3Ck0SHspB = "How would you characterize the online course?"

        if response and "choices" in response:
            labels = response["choices"].get('labels', [])
            total_reviewers += 1

            for label in labels:
                if label in tag_counts:
                    tag_counts[label] += 1

    tagdorsements_list = []
    if total_reviewers > 0:
        for tag, count in tag_counts.items():
            if count / total_reviewers > 0.66:
                tagdorsements_list.append(tag)

    tagdorsement_counts = json.dumps(tag_counts, cls=DjangoJSONEncoder)
    tagdorsements = ", ".join(tagdorsements_list)

    course.tagdorsement_counts=tagdorsement_counts
    course.tagdorsements=tagdorsements
    course.total_reviewers=total_reviewers
    course.save()
