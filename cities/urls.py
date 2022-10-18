from django.conf.urls import url

from .views import city_info
from .views import city_search
from .views import city_add

urlpatterns = [
    url(r'^search/$', city_search, name='api_city_search'),
    url(r'^(?P<place_id>[\d]+)/$', city_info, name='api_city_info'),
    url(r'$', city_add, name='api_city_add'),
]

