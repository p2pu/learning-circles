from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.LogPostView.as_view(), name='client_logging_logpost'),
]
