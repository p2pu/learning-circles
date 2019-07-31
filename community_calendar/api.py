from django.urls import reverse

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


class UserEventSerializer(serializers.HyperlinkedModelSerializer):
    """ for show a user their own events """
    edit_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()

    def get_edit_url(self, obj):
        return reverse('community_calendar_event_edit', args=[obj.pk])

    def get_delete_url(self, obj):
        return reverse('community_calendar_event_delete', args=[obj.pk])

    class Meta:
        model = Event
        fields = EventSerializer.Meta.fields + [
            'edit_url',
            'delete_url',
        ]


class EventViewSet(viewsets.ReadOnlyModelViewSet):

    def get_serializer_class(self):
        if self.request.user and self.request.query_params.get('user') == 'self':
            return UserEventSerializer
        return EventSerializer

    def get_queryset(self):
        if self.request.user and self.request.query_params.get('user') == 'self':
            return Event.objects.filter(created_by=self.request.user)
        if self.request.user and self.request.user.is_staff and self.request.query_parames.get('to_moderate') == 'yes':
            return Event.objects.to_moderate()
        return Event.objects.moderated()
