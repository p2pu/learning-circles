from django.conf.urls import url

from .views import city_info
from .views import city_search
from .views import city_add
from .views import country_search

urlpatterns = [
    url(r'^search/$', city_search, name='api_city_search'),
    url(r'^(?P<place_id>[\d]+)/$', city_info, name='api_city_info'),
    url(r'^search/country/$', country_search, name='api_country_search'),
    url(r'$', city_add, name='api_city_add'),
]

