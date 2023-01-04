from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from studygroups.models import StudyGroup
from places.models import City
from places.data import get_countries
from places.data import read_cities
from places.data import read_admin1_codes
from places.data import get_alternate_names

import requests
import csv

from pprint import pprint

def get_local_names(geonameid, name, language):
    alt_names = get_alternate_names(geonameid)
    alt_names = filter(lambda name_: name_['isPreferredName'] == '1', alt_names)
    alt_names = filter(lambda name_: name_['alternate name'] != name, alt_names)
    alt_names = filter(lambda name_: name_['isolanguage'] == language, alt_names)
    alt_names = list(alt_names)
    #if len(alt_names) > 0:
    #    print(f'name: \"{name}\", altname: \"{alt_names[0]["alternate name"]}\"')
    return alt_names


class Command(BaseCommand):
    help = 'Download and import city cities from geonames.org'

    def handle(self, *args, **options):
        cities = read_cities()
        # any city
        us_cities = list(filter(lambda city: city.get('feature code').startswith('PPL'), cities))
        # in the US
        us_cities = list(filter(lambda city: city.get('country code') == 'US', us_cities))
        # with more than 50,000 people
        us_cities = list(filter(lambda city: int(city.get('population')) > 50000, us_cities))
        admin_codes = read_admin1_codes()
        us_admin_codes = list(filter(lambda region: region.get('code').startswith('US'), admin_codes))
        print(len(us_cities))
        return

        for city in us_cities:
            region = next(filter(lambda region: region['code'] == f'{city["country code"]}.{city["admin1 code"]}', us_admin_codes), {'name': ''})

            data = {
                "city": city['name'],
                "region": region['name'],
                "country_en": 'United States of America',
                "country": 'United States of America',
                "latitude": city["latitude"], 
                "longitude": city["longitude"],
                "geonameid": city["geonameid"],
            }
            print(f'\n{data}')
            
            print(f'Search for city in db: {data}')
            matches = City.objects.filter(city=data['city'], region=data['region'], country=data['country'])
            if matches.count() == 1:
                print('** Found matching city in db, updating geonameid ')
                # Update geonameid
                matches.update(**data)
            else:
                print('** Adding city to db ')
                City.objects.create(**data)
