import hashlib
import hmac
import datetime


def check_webhook_signature(api_key, token, timestamp, signature):
    """ Check mailgun webhook signature """
    hmac_digest = hmac.new(
        key=bytes(api_key, 'latin-1'),
        msg=bytes('{}{}'.format(timestamp, token), 'latin-1'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, hmac_digest)


def parse_timestamp(timestamp_text):
     return datetime.datetime.strptime(timestamp_text, '%a, %d %b %Y %H:%M:%S GMT')
