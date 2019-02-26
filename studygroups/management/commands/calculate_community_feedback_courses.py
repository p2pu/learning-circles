from django.core.management.base import BaseCommand, CommandError

from studygroups.models import Course

class Command(BaseCommand):
    help = 'Calculate ratings and tagdorsements for courses based on Typeform survey responses'

    def handle(self, *args, **options):
        courses = Course.objects.filter(unlisted=False)
        for course in courses:
          course.calculate_ratings()
          course.calculate_tagdorsements()
          print("Saved community feedback for {}".format(course.title))
