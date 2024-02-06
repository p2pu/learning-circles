from django.db import models
from django.contrib.auth.models import User

class CourseList(models.Model):
    team = models.ForeignKey('studygroups.Team', on_delete=models.CASCADE)
    courses = models.ManyToManyField('studygroups.Course')

    def __str__(self):
        return f'{self.team.name} course list ({self.courses.count()})'


