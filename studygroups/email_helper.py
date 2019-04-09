from studygroups.utils import render_to_string_ctx
from premailer import Premailer
from django.conf import settings


def render_html_with_css(template, context):
    html = render_to_string_ctx(template, context)
    base_url = f"{settings.PROTOCOL}://{settings.DOMAIN}"
    html_with_inlined_css = Premailer(html, base_url=base_url, disable_validation=True).transform()
    return html_with_inlined_css


def render_email_templates(template_base, context):
    """ use template_base to render subject, text and html for email """
    # TODO make text template optional - use html to text when not specified
    subject = render_to_string_ctx(
        '{}-subject.txt'.format(template_base),
        context
    ).strip()
    txt = render_to_string_ctx(
        '{}.txt'.format(template_base),
        context
    )
    html = render_html_with_css(
        '{}.html'.format(template_base),
        context
    )
    return subject, txt, html
