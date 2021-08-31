from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_init

from announce.tasks import update_mailchimp_subscription


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


    @staticmethod
    def post_save(sender, **kwargs):
        instance = kwargs.get('instance')
        created = kwargs.get('created')
        if created or instance._communication_opt_in_old != instance.communication_opt_in:
            # NOTE user will be 'removed' from mailchimp if they create an account and didn't 
            # opt in. This is to cater for situations where a user previously subscribed to the
            # newsletter another way, but is only creating an account now
            update_mailchimp_subscription(instance.user_id)
            instance._communication_opt_in_old = instance.communication_opt_in

    @staticmethod
    def remember_state(sender, **kwargs):
        instance = kwargs.get('instance')
        instance._communication_opt_in_old = instance.communication_opt_in

    def __str__(self):
        return self.user.__str__()


post_save.connect(Profile.post_save, sender=Profile)
post_init.connect(Profile.remember_state, sender=Profile)
