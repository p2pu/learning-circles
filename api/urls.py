from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    url(r'^learningcircles/$', views.LearningCircleListView.as_view(), name='api_learningcircles'),
    url(r'^learningcircles/topics/$', views.LearningCircleTopicListView.as_view(), name='api_learningcircle_topics'),
    url(r'^courses/$', views.CourseListView.as_view(), name='api_courses'),
    url(r'^courses/topics/$', views.CourseTopicListView.as_view(), name='api_course_topics'),
    url(r'^signup/$', views.SignupView.as_view(), name='api_learningcircles_signup'),
    url(r'^learning-circle/$', views.LearningCircleCreateView.as_view(), name='api_learningcircles_create'),
    url(r'^learning-circle/(?P<study_group_id>[\d]+)/$', views.LearningCircleUpdateView.as_view(), name='api_learningcircles_update'),
    url(r'^landing-page-learning-circles/$', views.LandingPageLearningCirclesView.as_view(), name='api_learningcircles_meetings'),
    url(r'^landing-page-stats/$', views.LandingPageStatsView.as_view(), name='api_landing_page_stats'),
    url(r'^upload_image/$', views.ImageUploadView.as_view(), name='api_image_upload'),
]
