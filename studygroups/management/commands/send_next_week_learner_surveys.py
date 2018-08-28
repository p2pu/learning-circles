from django.core.management.base import BaseCommand, CommandError

from studygroups.models import send_learner_survey
from studygroups.models import StudyGroup

import datetime
from django.utils import timezone

class Command(BaseCommand):
    help = 'Send surveys to learners finishing in less than a week from now. This is to bridge the change in when surveys are sent and is not meant to be used otherwise.'

    def handle(self, *args, **options):
        # find all learner circles with the last meeting being less than a week in the future

        now = timezone.now()
        ## last :00, :15, :30 or :45 plus one week
        last_15 = now.replace(minute=now.minute//15*15, second=0)
        for study_group in StudyGroup.objects.published():
            last_meeting = study_group.meeting_set.active().order_by('-meeting_date', '-meeting_time').first()

            # send survey if last meeting is less than a week in the future
            if last_meeting and last_15 - datetime.timedelta(minutes=15) <= last_meeting.meeting_datetime() and last_meeting.meeting_datetime() < last_15 + datetime.timedelta(days=7):
                applications = study_group.application_set.active().filter(accepted_at__isnull=False).exclude(email='')
                timezone.deactivate()

                for application in applications:
                    send_learner_survey(application)


