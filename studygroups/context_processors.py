from django.conf import settings

def domain(request):
    return {
        'DOMAIN': settings.DOMAIN,
        'PROTOCOL': settings.PROTOCOL,
    }

def globals(request):
    return {
        'STATIC_SITE_URL': settings.STATIC_SITE_URL,
    }
