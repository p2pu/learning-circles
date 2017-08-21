from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^learningcircles/$', views.LearningCircleListView.as_view(), name='api_learningcircles'),
    url(r'^courses/$', views.CourseListView.as_view(), name='api_courses'),
    url(r'^signup/$', views.SignupView.as_view(), name='api_learningcircles_signup')
]

