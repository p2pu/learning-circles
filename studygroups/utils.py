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


import re
import bleach

def html_body_to_text(html):
    # rewrite links
    link_re = re.compile(r'<a.*?href="(?P<url>.*?)".*?>(?P<text>.*?)</a>')
    html = link_re.sub(r'\2 ( \1 ) ', html)
 
    # rewrite headings
    hx_re = re.compile(r'<h\d>(?P<text>.*?)</h\d>')
    html = hx_re.sub(r'# \1', html)

    # remove all HTML markup
    txt = bleach.clean(html, tags=[], strip=True)

    # remove leading and tailing whitespace and replace multiple newlines
    return re.sub(r'\n\s+', '\n\n', txt).strip()


