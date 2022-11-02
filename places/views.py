from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.postgres.search import SearchQuery
from django.contrib.postgres.search import SearchVector

import re
import json

from places.models import City
from uxhelpers.utils import json_response
from api import schema


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
    cities = City.objects.all()
    query = request.GET.get('query')
    if query:
        tsquery = CustomSearchQuery(query, config='simple')
        cities = cities.annotate(
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


def country_search(request):
    cities = City.objects.all()
    query = request.GET.get('query')
    if query:
        tsquery = CustomSearchQuery(query, config='simple')
        cities = City.objects.all().annotate(
            search = SearchVector(
                'country',
                'country_en',
                config='simple'
            )
        ).filter(search=tsquery)

    countries = cities.values('country', 'country_en').distinct('country_en', 'country').order_by('country')

    data = {
        "countries": list(countries)
    }
    return json_response(request, data)




@login_required
@require_http_methods(['POST'])
def city_add(request):
    post_schema = {
        "city": schema.text(required=True, length=256),
        "region": schema.text(required=True, length=256),
        "country": schema.text(required=True, length=256),
        "country_en": schema.text(required=True, length=256),
        "latitude": schema.floating_point(),
        "longitude": schema.floating_point()
    }

    data = json.loads(request.body)
    data, errors = schema.validate(post_schema, data)
    if errors != {}:
        return json_response(request, {"status": "error", "errors": errors})

    # TODO generate a place id?
    City.ojbects.create(data)
    return json_response(request, {"status": "created"})
