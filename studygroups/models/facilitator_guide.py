# coding=utf-8
from django.db import models
from django.contrib.auth.models import User

from .base import LifeTimeTrackingModel

class FacilitatorGuide(LifeTimeTrackingModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    study_group = models.ForeignKey('studygroups.StudyGroup', on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey('studygroups.Course', on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    caption = models.CharField(max_length=512)
    link = models.URLField()
    image = models.ImageField(blank=True)

    def __str__(self):
        return self.title
