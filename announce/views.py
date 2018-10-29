from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django import http
from django.contrib.auth.models import User

from .mailgun import check_webhook_signature
from .tasks import send_announcement

from email.utils import parseaddr, formataddr
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(['POST'])
def announce_webhook(request):
    """ This view is called by mailgun """
    # Verify mailgun call
    token = request.POST.get('token')
    timestamp = request.POST.get('timestamp')
    signature = request.POST.get('signature')
    authenticated = check_webhook_signature(settings.MAILGUN_API_KEY, token, timestamp, signature)
    if not authenticated:
        logger.warn('Authentication failed for announce_webhook')
        return http.HttpResponse(status=401) # TODO should this be 406 of just 200?

    # Get message details
    sender = request.POST.get('sender')
    from_ = request.POST.get('from')
    subject = request.POST.get('subject')
    body_text = request.POST.get('body-plain')
    body_html = request.POST.get('body-html')

    # Verify that email was sent from a staff user
    # parse sender to make sure it's not in the format John Silver <john@mail.net>
    user_name, user_email = parseaddr(sender)
    user = User.objects.filter(email=user_email).first()
    if not user or user.is_staff == False:
        logger.warn('Message sent to announce email from non-staff user')
        return http.HttpResponse(status=406)

    from_ = formataddr((user.first_name, settings.ANNOUNCE_EMAIL))

    # Send announcement message to all users that opted in
    send_announcement.delay(from_, subject, body_text, body_html)

    return http.HttpResponse(status=200)
