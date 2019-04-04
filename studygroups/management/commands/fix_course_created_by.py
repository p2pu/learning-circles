from django.core.management.base import BaseCommand, CommandError

from studygroups.models import Course
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Add a created_by field to all courses'

    def handle(self, *args, **options):
        user1 = User.objects.get(pk=1324)
        courses = Course.objects.filter(created_by__isnull=True, created_at__gt=user1.date_joined)
        courses.update(created_by=user1)
        courses = Course.objects.filter(created_by__isnull=True)
        courses.update(created_by=User.objects.get(pk=3))
