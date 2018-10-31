from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^send/$', views.announce_webhook, name='announce_webhook'),
]
