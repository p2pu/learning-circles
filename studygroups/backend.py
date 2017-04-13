from django.contrib.auth.backends import ModelBackend

class CaseInsensitiveBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        return super(CaseInsensitiveBackend, self).authenticate(username.lower(), password, **kwargs)
