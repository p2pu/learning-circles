from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^sso_redirect/$', views.discourse_sso, name='discourse_sso'),
]
