from django.urls import re_path

from .views import *

urlpatterns = [
    re_path(r'^event/add/$', EventCreate.as_view(), name='community_calendar_event_create'),
    re_path(r'^event/(?P<pk>[\d]+)/edit/$', EventUpdate.as_view(), name='community_calendar_event_edit'),
    re_path(r'^event/(?P<pk>[\d]+)/delete/$', EventDelete.as_view(), name='community_calendar_event_delete'),
    re_path(r'^event/(?P<pk>[\d]+)/moderate/$', EventModerate.as_view(), name='community_calendar_event_moderate'),
]
