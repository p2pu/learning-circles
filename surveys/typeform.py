from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import json
import requests
import logging
from dateutil import parser

from studygroups.models import StudyGroup

from .models import FacilitatorSurveyResponse

logger = logging.getLogger(__name__)


def get_form(form_id):
    url = 'https://api.typeform.com/forms/{}'.format(form_id)
    response = requests.get(
        url,
        headers={'Authorization': 'bearer {}'.format(settings.TYPEFORM_ACCESS_TOKEN)},
    )
    return response.json()


def get_all_responses(form_id, after=None):
    # NOTE: typeform doesn't paging, need to use after parameter, but no way 
    # to retrieve first token if len(responses) > 1000?
    # If there are < 1000 responses the first time this is run, and < 1000 between
    # polling intervals, this should be okay.
    url = 'https://api.typeform.com/forms/{}/responses'.format(form_id)
    params = {
        'page_size': 1000
    }
    if after:
        params['after'] = after
    print('&'.join(['{}={}'.format(k,v) for k,v in params.items()]))
    response = requests.get(
        url,
        params=params,
        headers={'Authorization': 'bearer {}'.format(settings.TYPEFORM_ACCESS_TOKEN)},
    )
    return response.json()


def sync_facilitator_responses():
    form_id = settings.TYPEFORM_FACILITATOR_SURVEY_FORM
    form = get_form(form_id)

    last_response = FacilitatorSurveyResponse.objects.order_by('-responded_at')\
        .first()
    after = None
    if last_response:
        after = last_response.typeform_key

    r = get_all_responses(form_id, after=after)

    print(r.get('total_items'))
    print(len(r.get('items', [])))
    for survey in r.get('items', []):
        study_group_id = survey.get('hidden').get('studygroup')
        study_group = None
        try:
            study_group = StudyGroup.objects.get(uuid=study_group_id)
        except ObjectDoesNotExist as e:
            logger.debug('Study group with ID does not exist', e)

        responded_at = parser.parse(survey.get('submitted_at'))
       
        data = {
            'study_group': study_group,
            'survey': json.dumps(form),
            'response': json.dumps(survey),
            'responded_at': responded_at
        }
        survey_response, created = FacilitatorSurveyResponse.objects.get_or_create(
            typeform_key=survey.get('token'),
            defaults=data
        )
        if not created:
            for attr, value in data.items():
                setattr(survey_response, attr, value)
            survey_response.save()


def sync_learner_responses():
    r = get_all_responses('VA1aVz')
    r.json()['items'][0]['hidden']['studygroup']
