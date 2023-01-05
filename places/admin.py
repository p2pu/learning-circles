from django.contrib import admin

from .models import City


class CityAdmin(admin.ModelAdmin):
    list_display = ['city', 'region', 'country', 'country_en', 'latitude', 'longitude']
    search_fields = ['city', 'region', 'country', 'country_en']


admin.site.register(City, CityAdmin)
