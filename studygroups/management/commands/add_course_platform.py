from django.core.management.base import BaseCommand, CommandError

from studygroups.models import Course

class Command(BaseCommand):
    help = 'Detect and save the course platform from the course URL'

    def handle(self, *args, **options):
        courses = Course.objects.all()
        for course in courses:
          if course.platform is None:
            course.detect_platform_from_link()
            print("Detected and saved platform for {}".format(course.title))
