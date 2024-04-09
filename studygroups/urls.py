from django.urls import include, re_path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from studygroups.views import MeetingCreate
from studygroups.views import MeetingUpdate
from studygroups.views import MeetingDelete
from studygroups.views import ApplicationCreateMultiple
from studygroups.views import ApplicationDelete
from studygroups.views import ApplicationUpdate
from studygroups.views import SignupSuccess
from studygroups.views import CoursePage
from studygroups.views import CourseReviewsPage
from studygroups.views import CourseCreate
from studygroups.views import CourseUpdate
from studygroups.views import CourseDelete
from studygroups.views import StudyGroupCreate
from studygroups.views import StudyGroupCreateLegacy
from studygroups.views import StudyGroupUpdate
from studygroups.views import StudyGroupUpdateLegacy
from studygroups.views import StudyGroupDelete
from studygroups.views import StudyGroupToggleSignup
from studygroups.views import StudyGroupPublish
from studygroups.views import StudyGroupList
from studygroups.views import StudyGroupLearnerSurvey
from studygroups.views import StudyGroupFacilitatorSurvey
from studygroups.views import StudyGroupDidNotHappen
from studygroups.views import LeaveTeam
from studygroups.views import TeamMembershipDelete
from studygroups.views import TeamInvitationCreate
from studygroups.views import InvitationConfirm
from studygroups.views import OptOutView
from studygroups.views import ExportSignupsView
from studygroups.views import ExportFacilitatorsView
from studygroups.views import ExportStudyGroupsView
from studygroups.views import ExportCoursesView
from studygroups.views import StaffDashView
from studygroups.views import StatsDashView
from studygroups.views import StudyGroupFinalReport
from studygroups.views import CommunityDigestView
from studygroups.views import DigestGenerateView
from studygroups.views import FacilitatorDashboard
from studygroups.views import OrganizerGuideForm
from studygroups.views import TeamUpdate
from studygroups.views import TeamCourseList
from studygroups.views import MessageView
from studygroups.views import MeetingRecap
from studygroups.views import MeetingRecapDismiss

from . import views

urlpatterns = [
    re_path(r'^$', FacilitatorDashboard.as_view(), name='studygroups_facilitator'),

    re_path(r'^courses/$', RedirectView.as_view(url='https://www.p2pu.org/en/courses/'), name='studygroups_courses'),

    re_path(r'^studygroups/$', views.studygroups, name='studygroups_search'),

    re_path(r'^login_redirect/$', views.login_redirect, name='studygroups_login_redirect'),

    re_path(r'^signup/(?P<location>[\w-]+)-(?P<study_group_id>[\d]+)/$', views.signup, name='studygroups_signup'),
    re_path(r'^signup/(?P<study_group_id>[\d]+)/success/$', SignupSuccess.as_view(), name='studygroups_signup_success'),

    re_path(r'^studygroup/create/$', StudyGroupCreate.as_view(), name='studygroups_facilitator_studygroup_create'),
    re_path(r'^studygroup/create/legacy/$', StudyGroupCreateLegacy.as_view(), name='studygroups_studygroup_create_legacy'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/$', views.view_study_group, name='studygroups_view_study_group'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/learn/$', views.StudyGroupParticipantView.as_view(), name='studygroups_view_learning_circle_participant'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/edit/$', StudyGroupUpdate.as_view(), name='studygroups_edit_study_group'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/edit/legacy/$', StudyGroupUpdateLegacy.as_view(), name='studygroups_studygroup_edit_legacy'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/delete/$', StudyGroupDelete.as_view(), name='studygroups_studygroup_delete'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/toggle_signup/$', StudyGroupToggleSignup.as_view(), name='studygroups_studygroup_toggle_signup'),

    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/publish/$', StudyGroupPublish.as_view(), name='studygroups_studygroup_publish'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/did_not_happen/$', StudyGroupDidNotHappen.as_view(), name='studygroups_studygroup_did_not_happen'),

    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/message/compose/$', views.message_send, name='studygroups_message_send'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/message/edit/(?P<message_id>[\d]+)/$', views.message_edit, name='studygroups_message_edit'),

    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/message/(?P<pk>[\d]+)/$', MessageView.as_view(), name='studygroups_message_view'),

    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/learner/add/$', views.add_learner, name='studygroups_add_learner'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/learner/add-multiple/$', ApplicationCreateMultiple.as_view(), name='studygroups_add_learners'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/learner/(?P<pk>[0-9]+)/edit/$', ApplicationUpdate.as_view(), name='studygroups_application_edit'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/learner/(?P<pk>[0-9]+)/delete/$', ApplicationDelete.as_view(), name='studygroups_application_delete',

    re_path(r'^studygroup/(?P<study_group_uuid>[\w-]+)/survey/$', StudyGroupLearnerSurvey.as_view(), name='studygroups_learner_survey'),
    re_path(r'^studygroup/(?P<study_group_uuid>[\w-]+)/survey/done/$', TemplateView.as_view(template_name='studygroups/learner_survey_done.html'), name='studygroups_learnear_survey_done'),
    re_path(r'^studygroup/(?P<study_group_uuid>[\w-]+)/facilitator_survey/$', StudyGroupFacilitatorSurvey.as_view(), name='studygroups_facilitator_survey'),
    re_path(r'^facilitator_survey/$', TemplateView.as_view(template_name='studygroups/anonymous_facilitator_survey.html'), name='anonymous_facilitator_survey'),
    re_path(r'^facilitator_survey/done/$', TemplateView.as_view(template_name='studygroups/facilitator_survey_done.html'), name='studygroups_facilitator_survey_done'),

    re_path(r'^studygroup/(?P<study_group_id>[\w-]+)/report/$', StudyGroupFinalReport.as_view(), name='studygroups_final_report'),

    # views regarding study group meetings
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<pk>[\d]+)/edit/$', MeetingUpdate.as_view(), name='studygroups_meeting_edit'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/create/$', MeetingCreate.as_view(), name='studygroups_meeting_create'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<pk>[0-9]+)/delete/$', MeetingDelete.as_view(), name='studygroups_meeting_delete'),


    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<pk>[\d]+)/recap/$', MeetingRecap.as_view(), name='studygroups_meeting_recap'),
    re_path(r'^studygroup/(?P<study_group_id>[\d]+)/meeting/(?P<pk>[\d]+)/recap/dismiss/$', MeetingRecapDismiss.as_view(), name='studygroups_meeting_recap_dismiss'),

    re_path(r'^course/create/$', CourseCreate.as_view(), name='studygroups_course_create'),
    re_path(r'^course/(?P<pk>[\d]+)/$', CoursePage.as_view(), name='studygroups_course_page'),
    re_path(r'^course/(?P<pk>[\d]+)/reviews/$', CourseReviewsPage.as_view(), name='studygroups_course_reviews_page'),
    re_path(r'^course/(?P<pk>[\d]+)/edit/$', CourseUpdate.as_view(), name='studygroups_course_edit'),
    re_path(r'^course/(?P<pk>[\d]+)/delete/$', CourseDelete.as_view(), name='studygroups_course_delete'),

    re_path(r'^facilitator/$', RedirectView.as_view(url='/'), name='studygroups_facilitator_deprecated'),
    re_path(r'^facilitator/team-invitation/$', InvitationConfirm.as_view(), name='studygroups_facilitator_invitation_confirm'),
    re_path(r'^facilitator/team-invitation/(?P<invitation_id>[\d]+)/$', InvitationConfirm.as_view(), name='studygroups_facilitator_invitation_confirm'),
    re_path(r'^facilitator/team-invitation/(?P<token>[\w-]+)/$', InvitationConfirm.as_view(), name='studygroups_facilitator_invitation_confirm_token'),
    re_path(r'^facilitator/teammembership/(?P<pk>[\d]+)/delete/$', LeaveTeam.as_view(), name='studygroups_facilitator_leave_team'),


    re_path(r'^optout/$', OptOutView.as_view(), name='studygroups_optout'),
    re_path(r'^optout/confirm/$', views.optout_confirm, name='studygroups_leave'),

    re_path(r'^rsvp/$', views.rsvp, name='studygroups_rsvp'),
    re_path(r'^rsvp/success/$', TemplateView.as_view(template_name='studygroups/rsvp_success.html'), name='studygroups_rsvp_success'),

    re_path(r'^organize/$', views.organize, name='studygroups_organize'),
    re_path(r'^organize/(?P<team_id>[\d]+)/$', views.organize_team, name='studygroups_organize_team'),
    re_path(r'^organize/studygroups/$', StudyGroupList.as_view(), name='studygroups_organizer_studygroup_list'),
    re_path(r'^organize/teammembership/(?P<team_id>[\d]+)/(?P<user_id>[\d]+)/delete/$', TeamMembershipDelete.as_view(), name='studygroups_teammembership_delete'),
    re_path(r'^organize/team/(?P<team_id>[\d]+)/member/invite/$', TeamInvitationCreate.as_view(), name='studygroups_team_member_invite'),
    re_path(r'^organize/team/(?P<team_id>[\d]+)/edit/$', TeamUpdate.as_view(), name='studygroups_team_edit'),
    re_path(r'^organize/team/(?P<team_id>[\d]+)/course_list/$', TeamCourseList.as_view(), name='studygroups_team_course_list'),

    re_path(r'^get-organizer-guide/$', OrganizerGuideForm.as_view(), name='studygroups_organizer_guide_form'),

    # These two URLs are deprecated, but kept for historic purposes
    re_path(r'^report/weekly/$', RedirectView.as_view(pattern_name='studygroups_weekly_update') ),
    re_path(r'^report/weekly/(?P<year>[\d]+)-(?P<month>[\d]+)-(?P<day>[\d]+)/$', RedirectView.as_view(pattern_name='studygroups_weekly_update_date')),

    re_path(r'^weekly-update/$', views.weekly_update, name='studygroups_weekly_update'),
    re_path(r'^weekly-update/(?P<year>[\d]+)-(?P<month>[\d]+)-(?P<day>[\d]+)/$', views.weekly_update, name='studygroups_weekly_update_date'),
    re_path(r'^weekly-update/(?P<team_id>[\d]+)/$', views.weekly_update, name='studygroups_weekly_update_team'),
    re_path(r'^weekly-update/(?P<team_id>[\d]+)/(?P<year>[\d]+)-(?P<month>[\d]+)-(?P<day>[\d]+)/$', views.weekly_update, name='studygroups_weekly_update_team_date'),

    re_path(r'^receive_sms/$', views.receive_sms, name='studygroups_receive_sms'),

    re_path(r'^staff/dash/$', StaffDashView.as_view(), name='studygroups_staff_dash'),
    re_path(r'^digest/generate/$', DigestGenerateView.as_view(), name='studygroups_digest_generate'),
    re_path(r'^staff/dash/stats/$', StatsDashView.as_view(), name='studygroups_staff_dash_stats'),

    re_path(r'^export/signups/$', ExportSignupsView.as_view(), name='studygroups_export_signups'),
    re_path(r'^export/facilitators/$', ExportFacilitatorsView.as_view(), name='studygroups_export_facilitators'),
    re_path(r'^export/studygroups/$', ExportStudyGroupsView.as_view(), name='studygroups_export_studygroups'),
    re_path(r'^export/courses/$', ExportCoursesView.as_view(), name='studygroups_export_courses'),

    re_path(r'^community_digest/(?P<start_date>[\w-]+)/(?P<end_date>[\w-]+)/$', CommunityDigestView.as_view(), name='studygroups_community_digest'),
]

