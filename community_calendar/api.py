from django.urls import reverse

from rest_framework import serializers, viewsets
from rest_framework import generics

import pytz
import datetime
from django.utils import timezone

from django.contrib.auth.models import User
from .models import Event


# Serializers define the API representation.

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name']


class EventSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

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
            'image',
            'created_by',
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
            'image',
            'edit_url',
            'delete_url',
        ]


class EventViewSet(viewsets.ReadOnlyModelViewSet):

    def get_serializer_class(self):
        if self.request.user.is_authenticated and self.request.query_params.get('user') == 'self':
            return UserEventSerializer
        return EventSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.query_params.get('user') == 'self':
            return Event.objects.filter(created_by=self.request.user)
        if self.request.user.is_authenticated and self.request.user.is_staff and self.request.query_params.get('to_moderate') == 'yes':
            return Event.objects.to_moderate()

        today = timezone.now()
        events = Event.objects.moderated().filter(datetime__gte=today).order_by('datetime')

        if 'limit' in self.request.GET:
            limit = int(self.request.GET.get('limit'))
            events = events[:limit]

        return events
