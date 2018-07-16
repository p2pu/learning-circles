from celery import shared_task
from .typeform import sync_facilitator_responses

@shared_task
def sync_facilitator_surveys():
    sync_facilitator_responses()
