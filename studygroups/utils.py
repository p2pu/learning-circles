from django.conf import settings

import urllib
import hmac
import hashlib

def gen_unsubscribe_querystring(user):
    qs = [
        ('user', user),
    ]
    sig = hmac.new(settings.SECRET_KEY, urllib.urlencode(qs), hashlib.sha256).hexdigest()
    qs.append( ('sig', sig) )
    return urllib.urlencode(qs)


def check_unsubscribe_signature(user, sig):
    qs = [
        ('user', user),
    ]
    return sig == hmac.new(settings.SECRET_KEY, urllib.urlencode(qs), hashlib.sha256).hexdigest()
