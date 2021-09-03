from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django import http
from django.contrib.auth.models import User

from .mailgun import check_webhook_signature
from .tasks import send_announcement
from studygroups.models import Profile

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

    from_name = '{0} from P2PU'.format(user.first_name)
    from_ = formataddr((from_name, settings.ANNOUNCE_EMAIL))

    # Send announcement message to all users that opted in
    send_announcement.delay(from_, subject, body_text, body_html)

    return http.HttpResponse(status=200)


@csrf_exempt
@require_http_methods(['POST'])
def mailchimp_webhook(request, webhook_secret):
    """ change profile.communications_opt_in if subscriber has an account """

    if webhook_secret != settings.MAILCHIMP_WEBHOOK_SECRET:
        return http.HttpResponse(status=404)

    list_id = request.POST.get('data[id]')
    if list_id != settings.MAILCHIMP_LIST_ID:
        logger.warning('mailchimp webhook called with invalid list id')
        return http.HttpResponse(status=404)

    email = request.POST.get('data[email]')
    if User.objects.filter(email__iexact=email).count() == 0:
        return http.HttpResponse(status=200)

    profile = Profile.objects.get(user__email=email)
    if request.POST.get('type') == 'unsubscribe':
        profile.communication_opt_in = False
    elif request.POST.get('type') == 'subscribe':
        profile.communication_opt_in = True
    profile.save()
    return http.HttpResponse(status=200)
