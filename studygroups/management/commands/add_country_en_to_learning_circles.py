from django.core.management.base import BaseCommand, CommandError

from studygroups.models import StudyGroup
import requests

class Command(BaseCommand):
    help = 'Ensure all learning circles have English country name'

    def handle(self, *args, **options):
        study_groups = StudyGroup.objects.active().exclude(place_id='')
        for study_group in study_groups:
            url = 'https://places-dsn.algolia.net/1/places/{}'.format(study_group.place_id)
            res = requests.get(url)
            if res.status_code != 200:
                print('Could not get place data for place_id {}. Response returned {}'.format(study_group.place_id, res.status_code))
                print('')
                continue
            country = res.json().get('country').get('default')
            country_en = res.json().get('country').get('en', None)

            if country_en is not None:
                study_group.country_en = country_en
            else:
                study_group.country_en = country

            study_group.save()
            print("Added country_en for study group {}: {}".format(study_group.id, study_group.country_en))

