from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from studygroups.models import StudyGroup
from cities.models import City

class Command(BaseCommand):
    help = 'Populate cities data based on current learning circles'

    def handle(self, *args, **options):
        study_groups = StudyGroup.objects.exclude(
            Q(place_id='')
            | Q(region='') 
            | Q(country='') 
            | Q(country_en='') 
            | Q(city='') 
        )
        
        places = study_groups.values('city', 'region', 'country', 'country_en', 'latitude', 'longitude', 'place_id').distinct('place_id', 'city').order_by('city')
        for place in places:
            print(place)
            City.objects.create(**place)



        

