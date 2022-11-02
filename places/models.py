from django.db import models


class City(models.Model):
    city = models.CharField(max_length=256)  # https://schema.org/addressLocality
    region = models.CharField(max_length=256, blank=True)  # https://schema.org/addressRegion
    country = models.CharField(max_length=256, blank=True)
    country_en = models.CharField(max_length=256, blank=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    place_id = models.CharField(max_length=256, blank=True)  # Algolia place_id
    geonameid = models.CharField(max_length=32, blank=True)  # Geoname.org geonameid

    class Meta:
        verbose_name_plural = "Cities"
