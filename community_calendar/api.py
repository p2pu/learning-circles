from rest_framework import serializers, viewsets
from rest_framework import generics

import pytz

from .models import Event

# Serializers define the API representation.
class EventSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Event
        fields = [
            'title',
             'description',
             'datetime',
             'local_datetime',
             'timezone',
             'city',
             'region',
             'country',
             'link',
             'image'
        ]


# ViewSets define the view behavior.
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all() #TODO .moderated()
    serializer_class = EventSerializer
