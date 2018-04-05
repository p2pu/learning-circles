from django.conf import settings

import urllib.request, urllib.parse, urllib.error
import hmac
import hashlib

# contact - email or mobile depending on contact preference
def gen_rsvp_querystring(contact, study_group, meeting_date, rsvp):
    qs = [
        ('user', contact),
        ('study_group', study_group),
        ('meeting_date', meeting_date.isoformat()),
        ('attending', rsvp)
    ]

    key = bytes(settings.SECRET_KEY, 'latin-1')
    data = bytes(urllib.parse.urlencode(qs), 'latin-1')
    sig = hmac.new(key, data, hashlib.sha256).hexdigest()
    qs.append( ('sig', sig) )
    return urllib.parse.urlencode(qs)


def check_rsvp_signature(contact, study_group, meeting_date, rsvp, sig):
    qs = [
        ('user', contact),
        ('study_group', study_group),
        ('meeting_date', meeting_date.isoformat()),
        ('attending', rsvp)
    ]
    key = bytes(settings.SECRET_KEY, 'latin-1')
    data = bytes(urllib.parse.urlencode(qs), 'latin-1')
    return sig == hmac.new(key, data, hashlib.sha256).hexdigest()

