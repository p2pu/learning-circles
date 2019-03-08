from celery import shared_task
from .typeform import sync_facilitator_responses
from .typeform import sync_learner_responses

@shared_task
def sync_surveys():
    new_facilitator_responses = sync_facilitator_responses()
    new_learner_responses = sync_learner_responses()
    affected_courses = set([r.study_group.course for r in new_facilitator_responses + new_learner_responses])
    for courses in affected_courses:
        course.calculate_ratings()
        course.calculate_tagdorsements()