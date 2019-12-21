# coding=utf-8
from django.db import models
from studygroups.models import StudyGroup
from studygroups.models import Application

import json

MAX_STAR_RATING = 5

class TypeformSurveyResponse(models.Model):
    typeform_key = models.CharField(max_length=64, unique=True) #Called token in the JSON response
    form_id = models.CharField(max_length=12)
    survey = models.TextField()
    response = models.TextField() #This will be a JSON value
    responded_at = models.DateTimeField()

    class Meta:
        abstract = True

    def get_response_field(self, question_id):
        response = json.loads(self.response)
        answers = response['answers']
        return next((answer for answer in answers if answer["field"]["id"] == question_id), None)

    def get_value_by_ref(self, ref):
        response = json.loads(self.response)
        answers = response.get('answers', [])
        answer = next((answer for answer in answers if answer["field"]["ref"] == ref), None)
        if not answer:
            return None
        type_ = answer.get('type')
        value = answer.get(type_)
        if type_ == 'choice':
            value = value.get('label')
        return value

    def get_survey_field(self, field_id):
        survey = json.loads(self.survey)
        survey_fields = survey['fields']
        return next((field for field in survey_fields if field["id"] == field_id), None)


class FacilitatorSurveyResponse(TypeformSurveyResponse):
    study_group = models.ForeignKey(StudyGroup, blank=True, null=True)


class LearnerSurveyResponse(TypeformSurveyResponse):
    study_group = models.ForeignKey(StudyGroup, blank=True, null=True)
    learner = models.ForeignKey(Application, blank=True, null=True)


def find_field(field_id, typeform_survey):
    """ look up field_id in survey """
    survey = typeform_survey
    fields = [ field for field in survey.get('fields') if field.get('id') == field_id ]
    field = None
    if len(fields) == 1:
        return fields[0]

    # check if field is part of a group?
    group_fields = [
        field.get('properties', {}).get('fields') for field in survey.get('fields') if field.get('type') == 'group'
    ]
    # group_fields = [ [field, field, field], [field, field]]
    # flatten list
    group_fields =  [item for sublist in group_fields for item in sublist]
    fields = [ field for field in group_fields if field.get('id') == field_id ]
    if len(fields) == 1:
        return fields[0]
    return None


def normalize_data(typeform_response):
    """
    Turn disjoint reponse and survey data from TypeForm into an dict with
    field id as key and an object with field title and answer as value
    """
    survey = json.loads(typeform_response.survey)
    response = json.loads(typeform_response.response)
    answers = {}
    for answer in response.get('answers', {}):
        field_id = answer.get('field').get('id')
        value_key = answer.get('type')
        value = json.dumps(answer.get(value_key))

        field = find_field(field_id, survey)
        field_title = field.get('title') if field else '??'

        answers[field_id] = {
            'field_title': field_title,
            'answer': value,
        }

    if typeform_response.study_group:
        answers['study_group_id'] = {
            'field_title': 'Learning circle ID',
            'answer': typeform_response.study_group.id,
        }
        answers['course'] = {
            'field_title': 'Course',
            'answer': typeform_response.study_group.course.title,
        }
        answers['facilitator'] = {
            'field_title': 'Facilitator',
            'answer': typeform_response.study_group.facilitator.email,
        }
        if hasattr(typeform_response.study_group.facilitator, 'teammembership'):
            answers['team'] = {
                'field_title': 'Team',
                'answer': typeform_response.study_group.facilitator.teammembership.team.name
            }

    return answers


def get_all_results(query_set):
    """ de-normalize all results into a single table structure """
    fields = {} # dict of all fields
    for response in query_set:
        data = normalize_data(response)
        # update headings
        for field_id, value in data.items():
            fields[field_id] = value.get('field_title')

    field_ids = fields.keys()
    heading = [fields[field_id] for field_id in field_ids]
    data = []
    for db in query_set:
        response = normalize_data(db)
        data += [
            [response.get(field_id, {}).get('answer', '') for field_id in field_ids]
        ]
    return {
        'heading': heading,
        'data': data
    }


def _transform_old_survey_data(survey_response):
    data = {
        "learned_extra": None,
        "confidence": None,
        "recommendation_rating": None,
        "recommendation_rating_reason": None,
    }

    # goal = signup goal OR survey goal OR None
    if survey_response.learner and survey_response.learner.get_goal():
        data['goal'] = survey_response.learner.get_goal()
    elif survey_response.get_value_by_ref('1929769b-dc20-4cd6-a849-c07ddd780456'):
        data['goal'] = survey_response.get_value_by_ref('1929769b-dc20-4cd6-a849-c07ddd780456')

    # goal_rating = application.goal_met or survey goal met x2

    # next_steps = survey next steps
    data['next_steps'] = survey_response.get_value_by_ref('3fa8908a-665d-4dfe-9d77-26a76294a253')

    # course rating = survey course rating
    # course rating reason = None
    return data


def get_learner_survey_data(survey_response):
    """
    Take a survey response, and return the following data:
    {
        "goal": "blah",
        "goal_rating": 1,
        "learned_extra": "nah",
        "subject_confidence": 1,
        "next_steps": "none",
        "course_rating": 4,
        "course_rating_reason": "blah",
        "recommendation_rating": 1,
        "recommendation_rating_reason": "blah",
    }
    """
    # TODO decide based on form ID how to get the data
    return _transform_old_survey_data(survey_response)
