from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from studygroups.views import StudyGroupUpdate
from studygroups.views import MeetingCreate
from studygroups.views import MeetingUpdate
from studygroups.views import MeetingDelete
from studygroups.views import FeedbackCreate
from studygroups.views import ApplicationDelete
from studygroups.views import SignupSuccess

from studygroups.decorators import user_is_group_facilitator

urlpatterns = patterns('',
    url(r'^$', 'studygroups.views.landing', name='studygroups_landing'),
    url(r'^signup/(?P<location>[\w-]+)-(?P<study_group_id>[\d]+)/$', 'studygroups.views.signup', name='studygroups_signup'),
    url(r'^signup/(?P<study_group_id>[\d]+)/success/$', SignupSuccess.as_view(), name='studygroups_signup_success'),
    url(r'^rsvp/$', 'studygroups.views.rsvp', name='studygroups_rsvp'),
    url(r'^rsvp/success/$', TemplateView.as_view(template_name='studygroups/rsvp_success.html'), name='studygroups_rsvp_success'),

    url(r'^facilitator/$', 'studygroups.views.facilitator', name='studygroups_facilitator'),

    url(r'^studygroup/(?P<study_group_id>[\d]+)/$', 'studygroups.views.view_study_group', name='studygroups_view_study_group'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/edit/$', user_is_group_facilitator(StudyGroupUpdate.as_view()), name='studygroups_edit_study_group'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/message/compose/$', 'studygroups.views.email', name='studygroups_email'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/message/edit/(?P<message_id>[\d]+)/$', 'studygroups.views.messages_edit', name='studygroups_messages_edit'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/member/add/$', 'studygroups.views.add_member', name='studygroups_add_member'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/member/(?P<pk>[0-9]+)/delete/$', login_required(ApplicationDelete.as_view()), name='studygroups_application_delete'),

    # views regarding study group meetings
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<pk>[\d]+)/edit/$', user_is_group_facilitator(MeetingUpdate.as_view()), name='studygroups_edit_study_group_meeting'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/create/$', user_is_group_facilitator(MeetingCreate.as_view()), name='studygroups_create_study_group_meeting'),
    url(r'studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<pk>[0-9]+)/delete/$', user_is_group_facilitator(MeetingDelete.as_view()), name='studygroups_meeting_delete'),           
   
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<study_group_meeting_id>[\d]+)/feedback/create/$', user_is_group_facilitator(FeedbackCreate.as_view()), name='studygroups_feedback'),

    url(r'^organize/$', 'studygroups.views.organize', name='studygroups_organize'),
    url(r'^report/$', 'studygroups.views.report', name='studygroups_report'),
    url(r'^receive_sms/$', 'studygroups.views.receive_sms', name='studygroups_receive_sms'),
)

