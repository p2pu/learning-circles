from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^city_complete/$', 'uxhelpers.views.city_complete', name='uxhelpers_city_complete'),
)

