from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', 'studygroups.views.landing', name='studygroups_landing'),
    url(r'^apply/$', 'studygroups.views.apply', name='studygroups_apply'),
    url(r'^organize/$', 'studygroups.views.organize', name='studygroups_organize'),
    url(r'^course/(?P<course_id>[\d]+)/$', 'studygroups.views.course', name='studygroups_course'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/signup/$', 'studygroups.views.signup', name='studygroups_signup'),
    url(r'^organize/studygroup/(?P<study_group_id>[\d]+)/email/$', 'studygroups.views.email', name='studygroups_email'),
)

