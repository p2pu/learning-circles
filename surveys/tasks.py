from celery import shared_task
from .typeform import sync_facilitator_responses
from .typeform import sync_learner_responses
from .community_feedback import calculate_course_ratings
from .community_feedback import calculate_course_tagdorsements

@shared_task
def sync_surveys():
    new_facilitator_responses = sync_facilitator_responses()
    new_learner_responses = sync_learner_responses()
    affected_courses = set([r.study_group.course for r in new_facilitator_responses + new_learner_responses if r.study_group and r.study_group.course])
    for courses in affected_courses:
        calculate_course_ratings(course)
        calculate_course_tagdorsements(course)
