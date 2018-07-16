# coding=utf-8
from django.db import models
from studygroups.models import StudyGroup
from studygroups.models import Application


class FacilitatorSurveyResponse(models.Model):
    typeform_key = models.CharField(max_length=64, unique=True) #Called token in the JSON response
    study_group = models.ForeignKey(StudyGroup, blank=True, null=True)
    survey = models.TextField()
    response = models.TextField() #This will be a JSON value
    responded_at = models.DateTimeField()
