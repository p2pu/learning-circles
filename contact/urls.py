from django.urls import re_path

from contact import views

urlpatterns = [
    re_path(r'^contact/$', views.ContactAPIView.as_view(), name='api_contact_form')
]
