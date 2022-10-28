from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from studygroups.models import StudyGroup
from cities.models import City
from cities.data import get_countries
from cities.data import read_cities
from cities.data import read_admin1_codes
from cities.data import get_alternate_names

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
    help = 'Download and import capital cities from geonames.org'

    def handle(self, *args, **options):
        countries = get_countries()
        cities = read_cities()
        capitals = list(filter(lambda city: city.get('feature code') == 'PPLC', cities))
        admin_codes = read_admin1_codes()
        print(len(capitals))
        print(len(list(countries)))
        for capital in capitals:
            country = next(filter(lambda country: country['ISO'] == capital['country code'], countries), None)
            if not country:
                print(f'Error: Could not find country for {capital}')
                continue
            region = next(filter(lambda region: region['code'] == f'{capital["country code"]}.{capital["admin1 code"]}', admin_codes), {'name': ''})
            #print(capital)
            #print(country)
            lang = country["Languages"].split(',')[0].split('-')[0]
            #print(f'\n{capital["name"]}, {region["name"]}, {country["Country"]}, {capital["latitude"]}, {capital["longitude"]} ({lang})')

            data = {
                "city": capital['name'],
                "region": region['name'],
                "country_en": country['Country'],
                "country": country['Country'],
                "latitude": capital["latitude"], 
                "longitude": capital["longitude"],
                "geonameid": capital["geonameid"],
            }
            print(f'\n{data}')

            capital_alt_names = get_local_names(capital['geonameid'], capital["name"], lang)
            #pprint(capital_alt_names)
            if len(capital_alt_names) == 1:
                data['city'] = capital_alt_names[0]['alternate name']
            
            if region.get('geonameid') and region.get('name'):
                region_alt_names = get_local_names(region['geonameid'], region['name'], lang)
                #pprint(region_alt_names)
                if len(region_alt_names) == 1:
                    data['region'] = region_alt_names[0]['alternate name']

            country_alt_names = get_local_names(country['geonameid'], country["Country"], lang)
            #pprint(country_alt_names)
            if len(country_alt_names) == 1:
                # TODO South Africa becomes iNingizimu Afrika - Zulu
                data['country'] = country_alt_names[0]['alternate name']

            print(f'Search for city in db: {data}')
            matches = City.objects.filter(city=data['city'], region=data['region'], country=data['country'])
            if matches.count() == 1:
                print('** Found matching city in db, updating geonameid ')
                # Update geonameid
                matches.update(geonameid = data['geonameid'])
            else:
                print('** Adding city to db ')
                City.objects.create(**data)


        return
        for country in countries:
            if not country["Capital"]:
                continue
            candidate_cities = filter(
                lambda city: city.get('asciiname') == country['Capital'] and city.get('country code') == country["ISO"],
                cities
            )
            if len(list(candidate_cities)) >= 1:
                continue

            print(f'\n\nTrouble getting capital info for {country["Capital"]}, {country["Country"]}')
            print(country)
            print(list(candidate_cities))

