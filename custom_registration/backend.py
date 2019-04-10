from django.contrib.auth.backends import ModelBackend

class CaseInsensitiveBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        return super(CaseInsensitiveBackend, self).authenticate(request, username.lower(), password, **kwargs)
