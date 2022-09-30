from django.db import models
from django.db.models import Count, Max, Q, Sum, Case, When, IntegerField, Value
from django.urls import reverse  # TODO ideally this shouldn't be in the model
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import F
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator


from .base import LifeTimeTrackingModel

import json

KNOWN_COURSE_PLATFORMS = {
    "www.edx.org/": "edX",
    "www.futurelearn.com/": "FutureLearn",
    "ocw.mit.edu/": "MIT OpenCourseWare",
    "www.coursera.org/": "Coursera",
    "www.khanacademy.org/": "Khan Academy",
    "www.lynda.com/": "Lynda",
    "oli.cmu.edu/": "Open Learning Initiative",
    "www.udemy.com/": "Udemy",
    "www.udacity.com/": "Udacity",
    "course.oeru.org/": "OERu",
    "www.open.edu/openlearn/": "OpenLearn",
    "www.codecademy.com/": "CodeAcademy",
}



def course_platform_from_url(url):
    platform = ""

    for domain in KNOWN_COURSE_PLATFORMS.keys():
        if domain in url:
            platform = KNOWN_COURSE_PLATFORMS[domain]

    return platform


class TopicGuide(models.Model):
    title = models.CharField(max_length=64)
    url = models.URLField()

    def __str__(self):
        return self.title


class Course(LifeTimeTrackingModel):
    RESOURCE_FORMATS = [
        ('course', 'Online Course'),
        ('book', 'Book'),
        ('video', 'Video'),
        ('article', 'Article'),
        ('group', 'Interest Group'),
        ('other', 'Other'),
    ] # TODO not sure I want to make this a enum/choice field ?

    OER_LICENSES = ['CC-BY', 'CC-BY-SA', 'CC-BY-NC', 'CC-BY-NC-SA', 'Public Domain']

    title = models.CharField(max_length=128)
    provider = models.CharField(max_length=256) # changed to creator in UI
    link = models.URLField()
    resource_format = models.CharField(max_length=128, choices=RESOURCE_FORMATS)
    caption = models.CharField(max_length=500)
    on_demand = models.BooleanField(default=False)
    keywords = models.CharField(max_length=500, blank=True) # changed to keyword in UI
    topic_guides = models.ManyToManyField(TopicGuide, blank=True, null=True)
    language = models.CharField(max_length=6) # ISO language code
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE) # TODO maybe rename to added_by
    unlisted = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    license = models.CharField(max_length=128, default="Not sure")
    platform = models.CharField(max_length=256, blank=True) # this field is deprecated, but kept for the API

    overall_rating = models.FloatField(default=0)                                # TODO
    total_ratings = models.SmallIntegerField(default=0)                          # TODO
    rating_step_counts = models.TextField(default="{}") # JSON value             # TODO
    discourse_topic_url = models.URLField(blank=True)

    def __str__(self):
        return self.title

    def keyword_list(self):
        return self.keywords.split(',')

    def rating_step_counts_json(self):
        return json.loads(self.rating_step_counts)

    def star_max(self):
        """ return the number of ratings attributed to the most popular rating """
        steps = self.rating_step_counts_json()
        return max(steps.values())

    def similar_courses(self):
        keywords = self.keywords.split(',')
        query = Q(keywords__icontains=keywordss[0])
        for keyword in keywords[1:]:
            query = Q(keywords__icontains=keyword) | query

        courses = Course.objects.filter(unlisted=False, deleted_at__isnull=True).filter(query).exclude(id=self.id).annotate(
            num_learning_circles=Sum(
                Case(
                    When(
                        studygroup__deleted_at__isnull=True, then=Value(1),
                        studygroup__course__id=F('id')
                    ),
                    default=Value(0), output_field=models.IntegerField()
                )
            )
        )[:3]

        return courses

    def discourse_topic_default_body(self):
        return _("<p>What recommendations do you have for other facilitators who are using \"{}\"? Consider sharing additional resources you found helpful, activities that worked particularly well, and some reflections on who this course is best suited for. For more information, see this course on <a href='https://learningcircles.p2pu.org{}'>P2PU’s course page</a>.</p>".format(self.title, reverse('studygroups_course_page', args=(self.id,))))

    def get_course_reviews(self):
        from studygroups.models import StudyGroup
        from surveys.models import FacilitatorSurveyResponse
        from surveys.models import facilitator_survey_summary

        facilitator_surveys = FacilitatorSurveyResponse.objects.filter(study_group__course=self)
        all_surveys = map(facilitator_survey_summary, facilitator_surveys)
        all_surveys = filter(lambda s: s.get('course_rating_reason'), all_surveys)

        return list(all_surveys)

    def get_num_of_facilitator_reviews(self):
        from studygroups.models import StudyGroup
        from surveys.models import FacilitatorSurveyResponse
        from surveys.models import facilitator_survey_summary

        studygroup_ids = StudyGroup.objects.filter(course=self.id).distinct().values_list("id", flat=True)
        facilitator_surveys = FacilitatorSurveyResponse.objects.filter(study_group__in=studygroup_ids)
        all_surveys = list(map(facilitator_survey_summary, facilitator_surveys))
        return len(all_surveys)

    def get_num_of_learner_reviews(self):
        from studygroups.models import StudyGroup
        from surveys.models import LearnerSurveyResponse
        from surveys.models import learner_survey_summary

        studygroup_ids = StudyGroup.objects.filter(course=self.id).distinct().values_list("id", flat=True)
        learner_surveys = LearnerSurveyResponse.objects.filter(study_group__in=studygroup_ids)
        all_surveys = list(map(learner_survey_summary, learner_surveys))
        return len(all_surveys)


