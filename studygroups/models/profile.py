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
    contact_url = models.URLField(max_length=256, blank=True)
    city = models.CharField(max_length=256, blank=True)
    region = models.CharField(max_length=256, blank=True) # schema.org. Algolia => administrative
    country = models.CharField(max_length=256, blank=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    place_id = models.CharField(max_length=256, blank=True) # Algolia place_id


    def __str__(self):
        return self.user.__str__()


