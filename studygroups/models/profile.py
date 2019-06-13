from django.db import models
from django.contrib.auth.models import User

# TODO move to custom_registration/models.py
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mailing_list_signup = models.BooleanField(default=False) # TODO remove this
    email_confirmed_at = models.DateTimeField(null=True, blank=True)
    interested_in_learning = models.CharField(max_length=500, blank=True)
    communication_opt_in = models.BooleanField(default=False)
    avatar = models.ImageField(blank=True)
    bio = models.TextField(max_length=500, blank=True)
    contact_url = models.CharField(max_length=256, blank=True)
    location = models.CharField(max_length=256, blank=True)


    def __str__(self):
        return self.user.__str__()


