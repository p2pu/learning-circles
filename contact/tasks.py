from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from celery import shared_task

from studygroups.email_helper import render_html_with_css
from studygroups.utils import html_body_to_text
from studygroups.utils import render_to_string_ctx


@shared_task
def send_contact_form_inquiry(email, name, content, source, organization=None):
    context = {
        "email": email,
        "name": name,
        "content": content,
        "source": source,
        "organization": organization,
    }

    subject_template = 'contact/contact_email-subject.txt'
    html_email_template = 'contact/contact_email.html'
    subject = render_to_string_ctx(subject_template, context).strip(' \n')
    html_body = render_html_with_css(html_email_template, context)
    text_body = html_body_to_text(html_body)

    to = [ settings.TEAM_EMAIL ]
    email = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        to,
        cc=[settings.SUPPORT_EMAIL],
        reply_to=[email, settings.SUPPORT_EMAIL]
    )
    email.attach_alternative(html_body, 'text/html')
    email.send()
