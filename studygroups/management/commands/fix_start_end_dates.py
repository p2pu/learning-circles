from django.core.management.base import BaseCommand, CommandError

from studygroups.models import StudyGroup

class Command(BaseCommand):
    help = 'Make sure all study groups with meetings have the correct start/end dates'

    def handle(self, *args, **options):
        for sg in StudyGroup.objects.active():
            if sg.meeting_set.active().count():
                start_date = sg.first_meeting().meeting_date
                end_date = sg.last_meeting().meeting_date
                if start_date != sg.start_date or end_date != sg.end_date:
                    sg.start_date = start_date
                    sg.end_date = end_date
                    sg.save()
                    print(f'Fixed start/end dates for {sg} starting {start_date} ending {end_date}')

