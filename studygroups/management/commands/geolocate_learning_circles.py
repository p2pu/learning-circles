from django.core.management.base import BaseCommand, CommandError

from cities.google import google_places_api
from cities import data
from studygroups.models import StudyGroup

class Command(BaseCommand):
    help = 'Find lat, lon for study groups without a position defined'

    def handle(self, *args, **options):
        study_groups = StudyGroup.objects.active().filter(
            latitude__isnull=True,
            longitude__isnull=True,
        ).exclude(city='')
        for study_group in study_groups:
            #print(study_group.course.title, study_group.city)
            city_data = study_group.city.split(',')
            city = city_data[0].strip() if len(city_data) > 0 else None
            region = city_data[1].strip() if len(city_data) > 1 else None
            country = city_data[2].strip() if len(city_data) > 2 else None
            results = data.find_city(city, region, country)
            if len(results) == 0:
                print(u'Could not find any cities matching: {}'.format(study_group.city))
                continue

            if len(results) > 1:
                print(u'Found more than one city matching: {}'.format(study_group.city))
                for i, opt in enumerate([u', '.join(cd[:3]) for cd in results]):
                    print(u'{}: {}'.format(i+1, opt))
                choice = raw_input('Please choose one: ')
                try:
                    choice = int(choice)-1
                    if choice > 0 and choice < len(results):
                        results = [results[choice]]
                except ValueError as e:
                    continue

            if len(results) != 1:
                continue

            print(u'update location for {}, lat={}, lon={}'.format(study_group.city, results[0][3], results[0][4]))
            study_group.latitude = results[0][3]
            study_group.longitude = results[0][4]
            study_group.save()

            #response = google_places_api(study_group.city)
            #results = response['results']
            #location = results[0]['geometry']['location']
            #study_group.latitude = location['lat']
            #study_group.longitude = location['lng']
