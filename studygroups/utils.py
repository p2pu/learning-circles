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


import re
import bleach

def html_body_to_text(html):
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
