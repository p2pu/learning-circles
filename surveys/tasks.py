from celery import shared_task
from .typeform import sync_facilitator_responses
from .typeform import sync_learner_responses

@shared_task
def sync_facilitator_surveys():
    sync_facilitator_responses()


@shared_task
def sync_learner_surveys():
    sync_learner_responses()
