from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=128)
    provider = models.CharField(max_length=256)
    link = models.URLField()
    start_date = models.DateField()
    duration = models.CharField(max_length=128)
    prerequisite = models.TextField()
    time_required = models.CharField(max_length=128)
    caption = models.TextField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title


class StudyGroup(models.Model):
    course = models.ForeignKey('studygroups.Course')
    location = models.CharField(max_length=128)
    location_link = models.URLField()
    time = models.CharField(max_length=128)
    max_size = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "Study group for " + self.course.title


class StudyGroupSignup(models.Model):
    study_group = models.ForeignKey('studygroups.StudyGroup')
    username = models.CharField(max_length=128)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.username

    class Meta:
        unique_together = ("email", "study_group")
