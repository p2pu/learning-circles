from django import template
from django.utils.text import slugify
from dateutil.parser import parse

from studygroups.models import TeamMembership

import datetime

register = template.Library()


@register.filter
def unicode_slugify(text):
    return slugify(text, allow_unicode=True)


@register.filter
def first_weekday_date(date):
    """
    Filter - returns the date of the first weekday for the date
    Usage (in template):
    {{ some_date|first_weekday_date }}
    """
    week_start = date - datetime.timedelta(days=date.weekday())
    return week_start.date()

@register.filter
def is_organizer(user):
    """
    Return true if the user is an organizer of staff
    """
    return user.is_staff or TeamMembership.objects.filter(user=user, role=TeamMembership.ORGANIZER)

@register.filter
def category_title(id, categories):
    category = next((category for category in categories if category["id"] == id), None)
    return category["name"]
