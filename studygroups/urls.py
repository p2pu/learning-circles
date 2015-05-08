from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', 'studygroups.views.landing', name='studygroups_landing'),
    url(r'^apply/$', 'studygroups.views.apply', name='studygroups_apply'),
    url(r'^organize/$', 'studygroups.views.organize', name='studygroups_organize'),
    url(r'^organize/studygroup/(?P<study_group_id>[\d]+)/email/$', 'studygroups.views.email', name='studygroups_email'),
    url(r'^receive_sms/$', 'studygroups.views.receive_sms', name='studygroups_receive_sms'),
)

