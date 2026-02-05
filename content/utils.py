import bleach

def clean_user_content(content):
    config = {
        'tags': ['table', 'tr', 'th', 'td', 'tbody', 'a', 'iframe'],
        'attributes': {'a': ['href'], 'iframe': ['src', 'width', 'height'] },
        'strip': True
    }
    content = bleach.clean(content, **config)
    #TODO ?? no idea why?
    return content
