from django.contrib import admin

# Register your models here.
from interest.models import Lead


class LeadAdmin(admin.ModelAdmin):
    pass

admin.site.register(Lead, LeadAdmin)

