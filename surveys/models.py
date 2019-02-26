# coding=utf-8
from django.db import models
from studygroups.models import StudyGroup
from studygroups.models import Application

import json


class FacilitatorSurveyResponse(models.Model):
    typeform_key = models.CharField(max_length=64, unique=True) #Called token in the JSON response
    study_group = models.ForeignKey(StudyGroup, blank=True, null=True)
    survey = models.TextField()
    response = models.TextField() #This will be a JSON value
    responded_at = models.DateTimeField()

    def get_response_field(self, question_id):
        response = json.loads(self.response)
        answers = response['answers']
        return next((answer for answer in answers if answer["field"]["id"] == question_id), None)

    def get_survey_field(self, field_id):
        survey = json.loads(self.survey)
        survey_fields = survey['fields']
        return next((field for field in survey_fields if field["id"] == field_id), None)



class LearnerSurveyResponse(models.Model):
    typeform_key = models.CharField(max_length=64, unique=True) #Called token in the JSON response
    study_group = models.ForeignKey(StudyGroup, blank=True, null=True)
    learner = models.ForeignKey(Application, blank=True, null=True)
    survey = models.TextField()
    response = models.TextField() #This will be a JSON value
    responded_at = models.DateTimeField()

    def get_response_field(self, question_id):
        response = json.loads(self.response)
        answers = response['answers']
        return next((answer for answer in answers if answer["field"]["id"] == question_id), None)

    def get_survey_field(self, field_id):
        survey = json.loads(self.survey)
        survey_fields = survey['fields']
        return next((field for field in survey_fields if field["id"] == field_id), None)


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
        # update headins
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

