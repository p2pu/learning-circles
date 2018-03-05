from django.conf import settings

import urllib.request, urllib.parse, urllib.error
import hmac
import hashlib

def gen_unsubscribe_querystring(user):
    qs = [
        ('user', user),
    ]
    key = bytes(settings.SECRET_KEY, 'latin-1')
    data = bytes(urllib.parse.urlencode(qs), 'latin-1')
    sig = hmac.new(key, data, hashlib.sha256).hexdigest()
    qs.append( ('sig', sig) )
    return urllib.parse.urlencode(qs)


def check_unsubscribe_signature(user, sig):
    qs = [
        ('user', user),
    ]
    key = bytes(settings.SECRET_KEY, 'latin-1')
    data = bytes(urllib.parse.urlencode(qs), 'latin-1')
    return sig == hmac.new(key, data, hashlib.sha256).hexdigest()
