from django.db import models

# Create your models here.
class Lead(models.Model):
    name = models.CharField(max_length=128)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=30, blank=True, null=True)
    course = models.CharField(max_length=1024, blank=True, null=True)
    location = models.CharField(max_length=1024, blank=True, null=True)
    time = models.CharField(max_length=1024, blank=True, null=True)
    source = models.CharField(max_length=1024, blank=True, null=True, verbose_name="Where did you hear about learning circles?")
    utm = models.CharField(max_length=1024, blank=True, null=True, verbose_name="UTM tracking data")

    created_at = models.DateTimeField(auto_now_add=True)
