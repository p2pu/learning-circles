from django.conf import settings
from django.template.loader import render_to_string

import urllib.request, urllib.parse, urllib.error
import hmac
import hashlib
import re
import bleach


def signed_querystring(params):
    key = bytes(settings.SECRET_KEY, 'latin-1')
    data = bytes(urllib.parse.urlencode(params), 'latin-1')
    sig = hmac.new(key, data, hashlib.sha256).hexdigest()
    qs.append( ('sig', sig) )
    return urllib.parse.urlencode(qs)


def check_signed_querystring(params, sig):
    key = bytes(settings.SECRET_KEY, 'latin-1')
    data = bytes(urllib.parse.urlencode(params), 'latin-1')
    return sig == hmac.new(key, data, hashlib.sha256).hexdigest()


def gen_unsubscribe_querystring(user):
    params = [
        ('user', user),
    ]
    return signed_querystring(params)


def check_unsubscribe_signature(user, sig):
    params = [
        ('user', user),
    ]
    return check_signed_querystring(params, sig)


# contact - email or mobile depending on contact preference
def gen_rsvp_querystring(contact, study_group, meeting_date, rsvp):
    params = [
        ('user', contact),
        ('study_group', study_group),
        ('meeting_date', meeting_date.isoformat()),
        ('attending', rsvp)
    ]
    return signed_querystring(params)


def check_rsvp_signature(contact, study_group, meeting_date, rsvp, sig):
    params = [
        ('user', contact),
        ('study_group', study_group),
        ('meeting_date', meeting_date.isoformat()),
        ('attending', rsvp)
    ]
    return check_signed_querystring(params, sig)


def render_to_string_ctx(template, context={}):
    context.update({
        'DOMAIN': settings.DOMAIN,
        'PROTOCOL': settings.PROTOCOL,
    })
    return render_to_string(template, context)


def html_body_to_text(html):
    """ Convern HTML email body to text """
    # Consider using https://github.com/aaronsw/html2text
    # remove style tags
    link_re = re.compile(r'<style>.*?</style>', re.MULTILINE|re.DOTALL)
    html = link_re.sub('', html)

    # rewrite links
    link_re = re.compile(r'<a.*?href="(?P<url>.*?)".*?>(?P<text>.*?)</a>')
    html = link_re.sub(r'\2 ( \1 ) ', html)
 
    # rewrite headings
    hx_re = re.compile(r'<h\d>(?P<text>.*?)</h\d>')
    html = hx_re.sub(r'# \1', html)

    # rewrite list items
    hx_re = re.compile(r'<li>(?P<text>.*?)</li>')
    html = hx_re.sub(r' - \1', html)

    # remove all HTML markup
    txt = bleach.clean(html, tags=[], strip=True)

    # remove leading and tailing whitespace and replace multiple newlines
    return re.sub(r'\n\s+', '\n\n', txt).strip()
