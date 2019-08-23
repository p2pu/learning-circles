from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.LogPostView.as_view(), name='client_logging_logpost'),
]
