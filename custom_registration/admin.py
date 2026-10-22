from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from studygroups.models import Profile

admin.site.unregister(Group)


class ProfileUserAdmin(UserAdmin):
    """ Ensure that users added through Django admin have an associated profile """

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            Profile.objects.get_or_create(user=obj)


admin.site.unregister(User)
admin.site.register(User, ProfileUserAdmin)
