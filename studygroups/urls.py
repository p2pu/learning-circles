from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from studygroups.views import MeetingCreate
from studygroups.views import MeetingUpdate
from studygroups.views import MeetingDelete
from studygroups.views import FeedbackDetail
from studygroups.views import FeedbackCreate
from studygroups.views import ApplicationDelete
from studygroups.views import SignupSuccess
from studygroups.views import CourseCreate
from studygroups.views import CourseUpdate
from studygroups.views import CourseDelete
from studygroups.views import StudyGroupCreate
from studygroups.views import StudyGroupUpdate
from studygroups.views import StudyGroupDelete
from studygroups.views import StudyGroupToggleSignup
from studygroups.views import StudyGroupList
from studygroups.views import StudyGroupMeetingList
from studygroups.views import TeamMembershipDelete
from studygroups.views import TeamInvitationCreate
from studygroups.views import FacilitatorSignup
from studygroups.views import FacilitatorSignupSuccess
from studygroups.views import FacilitatorStudyGroupCreate
from studygroups.views import InvitationConfirm
from studygroups.views import OptOutView
from studygroups.views import CourseListView
from studygroups.views import TeamPage

from studygroups.decorators import user_is_group_facilitator
from studygroups.decorators import user_is_organizer
from studygroups.decorators import user_is_not_logged_in

from . import views

urlpatterns = [
    url(r'^$', views.landing, name='studygroups_landing'),

    url(r'^courses/$', CourseListView.as_view(), name='studygroups_courses'),

    url(r'^city/(?P<city_name>[\w\W\ ,]+)/$', views.city, name='studygroups_city'),

    url(r'^studygroups/$', views.studygroups, name='studygroups_search'),

    url(r'^login_redirect/$', views.login_redirect, name='studygroups_login_redirect'),

    url(r'^signup/(?P<location>[\w-]+)-(?P<study_group_id>[\d]+)/$', views.signup, name='studygroups_signup'),
    url(r'^signup/(?P<study_group_id>[\d]+)/success/$', SignupSuccess.as_view(), name='studygroups_signup_success'),

    url(r'^studygroup/(?P<study_group_id>[\d]+)/$', views.view_study_group, name='studygroups_view_study_group'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/edit/$', user_is_group_facilitator(StudyGroupUpdate.as_view()), name='studygroups_edit_study_group'),
    url(r'^study_group/create/$', user_is_organizer(StudyGroupCreate.as_view()), name='studygroups_studygroup_create'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/delete/$', user_is_group_facilitator(StudyGroupDelete.as_view()), name='studygroups_studygroup_delete'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/toggle_signup/$', user_is_group_facilitator(StudyGroupToggleSignup.as_view()), name='studygroups_studygroup_toggle_signup'),

    url(r'^studygroup/(?P<study_group_id>[\d]+)/message/compose/$', views.message_send, name='studygroups_message_send'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/message/edit/(?P<message_id>[\d]+)/$', views.message_edit, name='studygroups_message_edit'),

    url(r'^studygroup/(?P<study_group_id>[\d]+)/member/add/$', views.add_member, name='studygroups_add_member'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/member/(?P<pk>[0-9]+)/delete/$', user_is_group_facilitator(ApplicationDelete.as_view()), name='studygroups_application_delete'),

    # views regarding study group meetings
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<pk>[\d]+)/edit/$', user_is_group_facilitator(MeetingUpdate.as_view()), name='studygroups_edit_study_group_meeting'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/create/$', user_is_group_facilitator(MeetingCreate.as_view()), name='studygroups_create_study_group_meeting'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<pk>[0-9]+)/delete/$', user_is_group_facilitator(MeetingDelete.as_view()), name='studygroups_meeting_delete'),           
   
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<study_group_meeting_id>[\d]+)/feedback/(?P<pk>[\d]+)/$', user_is_group_facilitator(FeedbackDetail.as_view()), name='studygroups_feedback_detail'),
    url(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<study_group_meeting_id>[\d]+)/feedback/create/$', user_is_group_facilitator(FeedbackCreate.as_view()), name='studygroups_feedback'),

    url(r'^course/create/$', login_required(CourseCreate.as_view()), name='studygroups_course_create'),
    url(r'^course/(?P<pk>[\d]+)/edit/$', user_is_organizer(CourseUpdate.as_view()), name='studygroups_course_edit'),
    url(r'^course/(?P<pk>[\d]+)/delete/$', user_is_organizer(CourseDelete.as_view()), name='studygroups_course_delete'),

    url(r'^facilitator/$', views.facilitator, name='studygroups_facilitator'),
    url(r'^facilitator/study_group/create/$', login_required(FacilitatorStudyGroupCreate.as_view()), name='studygroups_facilitator_studygroup_create'),
    url(r'^facilitator/signup/$', user_is_not_logged_in(FacilitatorSignup.as_view()), name='studygroups_facilitator_signup'),
    url(r'^facilitator/signup/success/$', FacilitatorSignupSuccess.as_view(), name='studygroups_facilitator_signup_success'),
    url(r'^facilitator/team-invitation/$', InvitationConfirm.as_view(), name='studygroups_facilitator_invitation_confirm'),

    url(r'^optout/$', OptOutView.as_view(), name='studygroups_optout'),
    url(r'^optout/confirm/$', views.optout_confirm, name='studygroups_leave'),

    url(r'^rsvp/$', views.rsvp, name='studygroups_rsvp'),
    url(r'^rsvp/success/$', TemplateView.as_view(template_name='studygroups/rsvp_success.html'), name='studygroups_rsvp_success'),

    url(r'^organize/$', views.organize, name='studygroups_organize'),
    url(r'^organize/(?P<team_id>[\d]+)/', views.organize_team, name='studygroups_organize_team'),
    url(r'^organize/studygroups/$', user_is_organizer(StudyGroupList.as_view()), name='studygroups_organizer_studygroup_list'),
    url(r'^organize/studygroup_meetings/$', user_is_organizer(StudyGroupMeetingList.as_view()), name='studygroups_organizer_studygroup_meetings'),
    url(r'^organize/teammembership/(?P<team_id>[\d]+)/(?P<user_id>[\d]+)/delete/$', user_is_organizer(TeamMembershipDelete.as_view()), name='studygroups_teammembership_delete'),
    url(r'^organize/team/(?P<team_id>[\d]+)/member/invite/$', TeamInvitationCreate.as_view(), name='studygroups_team_member_invite'),

    url(r'^report/weekly/$', views.weekly_report, name='studygroups_weekly_report'),
    url(r'^report/weekly/(?P<year>[\d]+)-(?P<month>[\d]+)-(?P<day>[\d]+)/$', views.weekly_report, name='studygroups_weekly_report_date'),

    url(r'^receive_sms/$', views.receive_sms, name='studygroups_receive_sms'),

    url(r'^(?P<slug>[\w-]+)/$', TeamPage.as_view(), name='studygroups_team_page'),
]

