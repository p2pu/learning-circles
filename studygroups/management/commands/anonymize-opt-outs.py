from django.core.management.base import BaseCommand, CommandError

from studygroups.models import Application

class Command(BaseCommand):
    help = 'Anonymize applications that previously opted out'

    def handle(self, *args, **options):
        applications = Application.objects.filter(deleted_at__isnull=False)
        print(f'About to anonymize {applications.count()} applications')
        for application in applications:
            application.anonymize()
