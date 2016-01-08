from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('analytics/ga_tracking_code.html')
def ga_tracking_code():
    return { 'GA_TRACKING_ID': settings.GA_TRACKING_ID }
