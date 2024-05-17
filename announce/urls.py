from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^send/$', views.announce_webhook, name='announce_webhook'),
    re_path(r'^mailchimp/(?P<webhook_secret>[\w-]+)$', views.mailchimp_webhook, name='announce_webhook'),
]
