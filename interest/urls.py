from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^sync/$', 'interest.views.sync', name='sync'),
)
