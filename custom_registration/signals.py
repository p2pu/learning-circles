from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

from .mailchimp import add_member_to_list
from .models import generate_user_token
from .models import send_email_confirm_email
from studygroups.models import Profile

@receiver(post_save, sender=Profile)
def handle_new_facilitator(sender, instance, created, **kwargs):
    if not created:
        return

    facilitator = instance
    user = instance.user

    # TODO - do this async
    send_email_confirm_email(user)


    # TODO - do this async
    # TODO - does this make sense to do before the email address is verified?
    # Add facilitator to Mailchimp newsletter

    if facilitator.communication_opt_in:
        add_member_to_list(facilitator.user)
