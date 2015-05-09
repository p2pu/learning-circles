from django.core.management.base import BaseCommand, CommandError

from studygroups.tasks import gen_reminders

class Command(BaseCommand):
    help = 'Generate reminders for all study groups happening in 3 days from now'

    def handle(self, *args, **options):
        gen_reminders()
