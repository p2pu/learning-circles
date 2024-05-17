# coding=utf-8
from django import forms
from django.utils.translation import gettext as _
from django.utils import timezone

from .models import Event

import pytz
import datetime
import logging

logger = logging.getLogger(__name__)

class EventForm(forms.ModelForm):
    TIMEZONES = [('', _('Select one of the following')),] + list(zip(pytz.common_timezones, pytz.common_timezones))

    timezone = forms.ChoiceField(choices=TIMEZONES, label=_('What timezone is the above time in?'))
    date = forms.DateField()
    time = forms.TimeField(input_formats=['%I:%M %p']) #TODO get this value as 24hr hh:mm:ss or hh:mm and localize in the UX

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['date'].initial = self.instance.local_datetime().date()
            self.fields['time'].initial = self.instance.local_datetime().time()

    def save(self, commit=True):
        event_datetime = datetime.datetime.combine(
            self.cleaned_data['date'],
            self.cleaned_data['time']
        )
        tz = pytz.timezone(self.cleaned_data['timezone'])
        self.instance.datetime = tz.localize(event_datetime)
        return super().save(commit)

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'date',
            'time',
            'timezone',
            'city',
            'region',
            'country',
            'country_en',
            'link',
            'image'
        ]
        labels = {
            'datetime': _('Event date and time'),
        }
        help_texts = {
            'description': _('This description will appear on p2pu.org/events. Maximum 500 characters.'),
            'city': _('Is this event happing in a specific location?'),
            'link': _('This is where you should direct people to sign up. If you don’t have a website, you can create a post on our community forum.'),
            'image': _('Make your learning circle stand out with a picture or .gif. It could be related to location, subject matter, or anything else you want to identify with!'),
        }
        widgets = {
            'latitude': forms.HiddenInput,
            'longitude': forms.HiddenInput,
            'place_id': forms.HiddenInput,
            'country': forms.HiddenInput,
            'country_en': forms.HiddenInput,
            'region': forms.HiddenInput,
            'datetime': forms.HiddenInput,
            'description': forms.Textarea(attrs={"rows":5}),
        }

class EventModerateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'moderation_note',
        ]
        widgets = {
            'moderation_note': forms.Textarea(attrs={"rows":5}),
        }

    def save(self, commit=True):
        event = super().save(commit)
        event.moderation_approved = self.data['moderation_approved'] == 'yes'
        if commit:
            event.save()
        return event


