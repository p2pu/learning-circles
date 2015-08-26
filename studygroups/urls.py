from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', 'studygroups.views.landing', name='studygroups_landing'),
    url(r'^signup/(?P<location>[\w-]+)-(?P<study_group_id>[\d]+)/$', 'studygroups.views.signup', name='studygroups_signup'),
    url(r'^rsvp/$', 'studygroups.views.rsvp', name='studygroups_rsvp'),

    url(r'^facilitator/$', 'studygroups.views.facilitator', name='studygroups_facilitator'),
    url(r'^study_group/(?P<study_group_id>[\d]+)/$', 'studygroups.views.view_study_group', name='studygroups_view_study_group'),
    
    url(r'^organize/$', 'studygroups.views.organize', name='studygroups_organize'),
    url(r'^organize/studygroup/(?P<study_group_id>[\d]+)/message/compose/$', 'studygroups.views.email', name='studygroups_email'),
    url(r'^organize/studygroup/(?P<study_group_id>[\d]+)/message/edit/(?P<message_id>[\d]+)/$', 'studygroups.views.messages_edit', name='studygroups_messages_edit'),
    url(r'^organize/studygroup/(?P<study_group_id>[\d]+)/message/list/$', 'studygroups.views.organize_messages', name='studygroups_organize_messages'),
    url(r'^receive_sms/$', 'studygroups.views.receive_sms', name='studygroups_receive_sms'),
)

