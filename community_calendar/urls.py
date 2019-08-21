from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^event/add/$', EventCreate.as_view(), name='community_calendar_event_create'),
    url(r'^event/(?P<pk>[\d]+)/edit/$', EventUpdate.as_view(), name='community_calendar_event_edit'),
    url(r'^event/(?P<pk>[\d]+)/delete/$', EventDelete.as_view(), name='community_calendar_event_delete'),
    url(r'^event/(?P<pk>[\d]+)/moderate/$', EventModerate.as_view(), name='community_calendar_event_moderate'),
]
