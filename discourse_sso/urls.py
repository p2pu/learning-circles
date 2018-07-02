from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^sso_redirect/$', views.discourse_sso, name='discourse_sso'),
]
