from django.contrib import admin

from .models import City


class CityAdmin(admin.ModelAdmin):
    list_display = ['city', 'region', 'country', 'country_en', 'latitude', 'longitude']


admin.site.register(City, CityAdmin)
