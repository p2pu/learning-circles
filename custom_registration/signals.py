from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

from .models import send_email_confirm_email
from studygroups.models import Profile

@receiver(post_save, sender=Profile)
def handle_new_facilitator(sender, instance, created, **kwargs):
    if not created:
        return

    profile = instance
    # TODO - do this async
    send_email_confirm_email(profile.user)
