from django.contrib import admin

# Register your models here.
from .models import Event

class EventAdmin(admin.ModelAdmin):

    list_display = ['datetime', 'title', 'created_by']
    raw_id_fields = ("created_by",)



admin.site.register(Event, EventAdmin)
