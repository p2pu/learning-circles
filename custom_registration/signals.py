from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings

from .mailchimp import add_member_to_list
from studygroups.models import Facilitator

@receiver(post_save, sender=Facilitator)
def handle_new_facilitator(sender, instance, created, **kwargs):
    if not created:
        return

    facilitator = instance
    user = instance.user

    # TODO - do this async
    reset_form = PasswordResetForm({'email': user.email})
    if not reset_form.is_valid():
        raise Exception(reset_form.errors)

    reset_form.save(
        subject_template_name='studygroups/email/facilitator_created-subject.txt',
        email_template_name='studygroups/email/facilitator_created.txt',
        html_email_template_name='studygroups/email/facilitator_created.html',
        domain_override=settings.DOMAIN,
        from_email=settings.SERVER_EMAIL,
    )

    # TODO - do this async
    # Add facilitator to Mailchimp newsletter
    if facilitator.mailing_list_signup:
        add_member_to_list(facilitator.user)
