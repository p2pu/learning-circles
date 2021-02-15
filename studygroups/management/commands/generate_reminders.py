from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from studygroups.models import Meeting
from studygroups.models.learningcircle import generate_meeting_reminder

class Command(BaseCommand):
    help = 'Transitional command to generate reminders for all meetings in the future.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        meetings = Meeting.objects.active().filter(study_group__deleted_at__isnull=True).filter(meeting_date__gte=today)
        for meeting in meetings:
            print(f'Generating meeting reminder for meeting happening {meeting.meeting_date}')
            generate_meeting_reminder(meeting)
