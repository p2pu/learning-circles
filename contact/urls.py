from django.conf.urls import url

from contact import views

urlpatterns = [
    url(r'^contact/$', views.ContactAPIView.as_view(), name='api_contact_form')
]
