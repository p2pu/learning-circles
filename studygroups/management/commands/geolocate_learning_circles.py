from django.core.management.base import BaseCommand, CommandError

from cities.google import google_places_api
from cities import data
from studygroups.models import StudyGroup
import requests

class Command(BaseCommand):
    help = 'Complete location data based on Algolia API'

    def handle(self, *args, **options):
        study_groups = StudyGroup.objects.active().filter(country='').exclude(place_id='')
        for study_group in study_groups:
            print(study_group.course.title, study_group.city)
            url = 'https://places-dsn.algolia.net/1/places/{}'.format(study_group.place_id)
            res = requests.get(url)
            if res.status_code != 200:
                print('Could not get place data for place_id {}. Response returned {}'.format(study_group.place_id, res.status_code))
                print('')
                continue
            country = res.json().get('country').get('default')
            region = res.json().get('administrative')[0]
            city = res.json().get('locale_names').get('default')[0]
            study_group.country = country
            study_group.region = region
            if city != study_group.city:
                study_group.city = city
            study_group.save()
            print(', '.join([city, region, country]))
            print('')

