from django.contrib.postgres.search import SearchQuery
from django.contrib.postgres.search import SearchVector

import re

from cities.models import City
from uxhelpers.utils import json_response


# TODO copypasta from studygroups.views.api
class CustomSearchQuery(SearchQuery):

    """ NOTE: This is potentially unsafe!!"""
    def __init__(self, value, search_type='raw', **kwargs):
        # update passed in value to support prefix matching
        query = re.sub(r'[!\'()|&\:=,\.\ \-\<\>@]+', ' ', value).strip().lower()
        tsquery = ":* & ".join(query.split(' '))
        tsquery += ":*"
        super().__init__(tsquery, search_type=search_type, **kwargs) 


def city_info(request, place_id):
    place = City.objects.filter(place_id=place_id).values('city', 'region', 'country', 'country_en', 'latitude', 'longitude', 'place_id').first()
    return json_response(request, place)


def city_search(request):
    query = request.GET.get('query')

    tsquery = CustomSearchQuery(query, config='simple')
    cities = City.objects.all().annotate(
        search = SearchVector(
            'city',
            'region',
            'country',
            'country_en',
            config='simple'
        )
    ).filter(search=tsquery)

    places = cities.values('city', 'region', 'country', 'country_en', 'latitude', 'longitude', 'place_id').distinct('city', 'region', 'country').order_by('city')

    data = {
        "cities": list(places)
    }
    return json_response(request, data)
