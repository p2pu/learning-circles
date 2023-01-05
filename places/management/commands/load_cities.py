from django.core.management.base import BaseCommand, CommandError

from places.models import City

import json
import requests


class Command(BaseCommand):
    help = 'Download and import city cities from geonames.org'

    def handle(self, *args, **options):

        UPDATE_URL = 'https://raw.githubusercontent.com/p2pu/learning-circles/places/us_cities50k.json'
        resp = requests.get(UPDATE_URL)
        us_cities = resp.json()

        for city in us_cities:
            print(f'Search for city in db: {city}')
            matches = City.objects.filter(city=city['city'], region=city['region'], country=city['country'])
            if matches.count() == 1:
                print('** Found matching city in db, updating geonameid ')
                # Update geonameid
                matches.update(**city)
            else:
                print('** Adding city to db ')
                City.objects.create(**city)
