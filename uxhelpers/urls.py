from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^city_complete/$', views.city_complete, name='uxhelpers_city_complete'),
]
