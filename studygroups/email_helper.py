from django.template.loader import render_to_string

def render_email_templates(template_base, context):
    """ use template_base to render subject, text and html for email """
    # TODO make text template optional - use html to text when not specified
    subject = render_to_string(
        '{}-subject.txt'.format(template_base),
        context
    ).strip()
    txt = render_to_string(
        '{}.txt'.format(template_base),
        context
    )
    html = render_to_string(
        '{}.html'.format(template_base),
        context
    )
    return subject, txt, html
