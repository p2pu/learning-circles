from django.core.management.base import BaseCommand, CommandError

from studygroups.tasks import send_reminders

class Command(BaseCommand):
    help = 'Send reminders for all study groups happening in 2 days from now'

    def handle(self, *args, **options):
        send_reminders()
