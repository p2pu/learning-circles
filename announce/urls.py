from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^send/$', views.announce_webhook, name='announce_webhook'),
    url(r'^mailchimp/(?P<webhook_secret>[\w-]+)$', views.mailchimp_webhook, name='announce_webhook'),
]
