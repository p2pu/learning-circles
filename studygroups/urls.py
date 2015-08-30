from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from studygroups.views import MeetingCreate
from studygroups.views import MeetingDelete

urlpatterns = patterns('',
    url(r'^$', 'studygroups.views.landing', name='studygroups_landing'),
    url(r'^signup/(?P<location>[\w-]+)-(?P<study_group_id>[\d]+)/$', 'studygroups.views.signup', name='studygroups_signup'),
    url(r'^rsvp/$', 'studygroups.views.rsvp', name='studygroups_rsvp'),

    url(r'^facilitator/$', 'studygroups.views.facilitator', name='studygroups_facilitator'),

    url(r'^studygroup/(?P<study_group_id>[\d]+)/edit/$', 'studygroups.views.edit_study_group', name='studygroups_edit_study_group'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/$', 'studygroups.views.view_study_group', name='studygroups_view_study_group'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/message/compose/$', 'studygroups.views.email', name='studygroups_email'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/message/edit/(?P<message_id>[\d]+)/$', 'studygroups.views.messages_edit', name='studygroups_messages_edit'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/message/list/$', 'studygroups.views.organize_messages', name='studygroups_organize_messages'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/member/add/$', 'studygroups.views.add_member', name='studygroups_add_member'),

    # views regarding study group meetings
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<study_group_meeting_id>[\d]+)/edit/$', 'studygroups.views.edit_study_group_meeting', name='studygroups_edit_study_group_meeting'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/create/$', MeetingCreate.as_view(), name='studygroups_create_study_group_meeting'),
    url(r'studygroup/meeting/(?P<pk>[0-9]+)/delete/$', MeetingDelete.as_view(), name='studygroups_meeting_delete'),           
   
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<study_group_meeting_id>[\d]+)/feedback/$', 'studygroups.views.feedback', name='studygroups_feedback'),

    url(r'^organize/$', 'studygroups.views.organize', name='studygroups_organize'),
    url(r'^receive_sms/$', 'studygroups.views.receive_sms', name='studygroups_receive_sms'),
)

