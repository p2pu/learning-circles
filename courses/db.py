from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=255)
    short_title = models.CharField(max_length=20)
    description = models.CharField(max_length=1000)
    language = models.CharField(max_length=32)
    image_uri = models.CharField(max_length=256)
    creation_date = models.DateTimeField(auto_now_add=True)
    draft = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    creator_uri = models.CharField(max_length=256)
    based_on = models.ForeignKey('courses.Course', models.SET_NULL, related_name='derived_courses', blank=True, null=True)


class CourseContent(models.Model):
    course = models.ForeignKey(Course, models.CASCADE, related_name='content')
    content_uri = models.CharField(max_length=256) 
    index = models.PositiveIntegerField()


class CourseTags(models.Model):
    course = models.ForeignKey(Course, models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=64)
