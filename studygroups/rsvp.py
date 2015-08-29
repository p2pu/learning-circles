from django.conf import settings

import urllib
import urlparse
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
    sig = hmac.new(settings.SECRET_KEY, urllib.urlencode(qs), hashlib.sha256).hexdigest()
    qs.append( ('sig', sig) )
    return urllib.urlencode(qs)


def check_rsvp_signature(contact, study_group, meeting_date, rsvp, sig):
    qs = [
        ('user', contact),
        ('study_group', study_group),
        ('meeting_date', meeting_date.isoformat()),
        ('attending', rsvp)
    ]
    return sig == hmac.new(settings.SECRET_KEY, urllib.urlencode(qs), hashlib.sha256).hexdigest()

