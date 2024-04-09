from django.urls import re_path

from .views import city_info
from .views import city_search
from .views import city_add
from .views import country_search

urlpatterns = [
    re_path(r'^search/city/$', city_search, name='api_city_search'),
    re_path(r'^search/country/$', country_search, name='api_country_search'),
    re_path(r'^(?P<place_id>[\d]+)/$', city_info, name='api_city_info'),
]
