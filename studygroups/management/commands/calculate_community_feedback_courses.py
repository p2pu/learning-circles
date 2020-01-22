from django.core.management.base import BaseCommand, CommandError

from studygroups.models import Course
from surveys.community_feedback import calculate_course_ratings

class Command(BaseCommand):
    help = 'Calculate ratings for courses based on Typeform survey responses'

    def handle(self, *args, **options):
        courses = Course.objects.filter(unlisted=False)
        for course in courses:
          calculate_course_ratings(course)
          print("Saved community feedback for {}".format(course.title))
