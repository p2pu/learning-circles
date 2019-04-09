from django.conf import settings

def domain(request):
    return {
        'DOMAIN': settings.DOMAIN,
        'PROTOCOL': settings.PROTOCOL,
    }
