from django.core.management.base import BaseCommand, CommandError

from studygroups.models import StudyGroup
import requests

class Command(BaseCommand):
    help = 'Associate learning circles to the team of the facilitator'

    def handle(self, *args, **options):
        study_groups = StudyGroup.objects.active()
        for study_group in study_groups:
            if study_group.facilitator.teammembership_set.active().count():
                study_group.team = study_group.facilitator.teammembership_set.active().first().team
                study_group.save()
                print("Added study group to team {}: {}".format(study_group.id, study_group.team_id))

