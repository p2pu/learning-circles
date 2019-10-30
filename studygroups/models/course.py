from django.db import models
from django.db.models import Count, Max, Q, Sum, Case, When, IntegerField, Value
from django.urls import reverse  # TODO ideally this shouldn't be in the model
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from .base import LifeTimeTrackingModel

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


class Course(LifeTimeTrackingModel):
    OER_LICENSES = ['CC-BY', 'CC-BY-SA', 'CC-BY-NC', 'CC-BY-NC-SA', 'Public Domain']

    title = models.CharField(max_length=128)
    provider = models.CharField(max_length=256)
    link = models.URLField()
    caption = models.CharField(max_length=500)
    on_demand = models.BooleanField()
    topics = models.CharField(max_length=500)
    language = models.CharField(max_length=6) # ISO language code
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    unlisted = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    license = models.CharField(max_length=128, blank=True)
    platform = models.CharField(max_length=256, blank=True)

    overall_rating = models.FloatField(default=0)
    total_ratings = models.SmallIntegerField(default=0)
    rating_step_counts = models.TextField(default="{}") # JSON value
    tagdorsements = models.CharField(max_length=256, blank=True)
    tagdorsement_counts =  models.TextField(default="{}") # JSON value
    total_reviewers = models.SmallIntegerField(default=0)
    discourse_topic_url = models.URLField(blank=True)

    def __str__(self):
        return self.title

    def similar_courses(self):
        topics = self.topics.split(',')
        query = Q(topics__icontains=topics[0])
        for topic in topics[1:]:
            query = Q(topics__icontains=topic) | query

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

    def detect_platform_from_link(self):
        platform = course_platform_from_url(self.link)

        self.platform = platform
        self.save()

    def discourse_topic_default_body(self):
        return _("<p>What recommendations do you have for other facilitators who are using \"{}\"? Consider sharing additional resources you found helpful, activities that worked particularly well, and some reflections on who this course is best suited for. For more information, see this course on <a href='https://learningcircles.p2pu.org{}'>P2PU’s course page</a>.</p>".format(self.title, reverse('studygroups_course_page', args=(self.id,))))
