from django.core.management.base import BaseCommand, CommandError

from studygroups.models import Course
from studygroups.models import TopicGuide
import requests

class Command(BaseCommand):
    help = 'Fetch course updates from remote URL and apply them'

    def handle(self, *args, **options):
        guides = TopicGuide.objects.all()
        courses = Course.objects.active()
        for course in courses:
            keywords = [t.lower().strip() for t in course.keywords.split(',')]
            course_guides = [guide for guide in guides if guide.slug in keywords]
            if course_guides:
                print(f'Adding {course_guides} to {course}')
                course.topic_guides.add(*course_guides)
