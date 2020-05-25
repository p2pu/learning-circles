from django.core.management.base import BaseCommand, CommandError

from studygroups.models import StudyGroup, Course

class Command(BaseCommand):
    help = 'Reset generated learning circle name to course title'

    def handle(self, *args, **options):
        for sg in StudyGroup.objects.all():
            course = Course.objects.filter(pk=int(sg.course.id)).first()
            if course is None:
                print("Studygroup {} uses a course that no longer exists: {}".format(sg.id, sg.course.title))
                sg.name = 'Untitled'

            course_title = course.title[:64]
            print("Renaming {} to {}".format(sg.name, course_title))
            sg.name = course_title
            sg.save()