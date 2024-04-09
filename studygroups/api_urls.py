from django.urls import re_path
from django.conf.urls import include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from rest_framework.routers import DefaultRouter

from . import views

from .views import drf

router = DefaultRouter()
router.register(r'meeting_feedback', drf.FeedbackViewSet)
router.register(r'learningcircle_feedback', drf.StudyGroupRatingViewSet, basename='learningcircle_feedback')
router.register(r'team_invitation', drf.TeamInvitationViewSet, basename='team_invitations')
router.register(r'team_membership', drf.TeamMembershipViewSet, basename='team_membership')
router.register(r'member_learningcircles', drf.MemberLearningCircleViewSet, basename='member_learningcircles')
router.register(r'course_list', drf.CourseListViewSet, basename='course_list')

# TODO split / indicate what is used on www.p2pu.org vs what is used for management UX

urlpatterns = [
    re_path(r'^learningcircles/$', views.LearningCircleListView.as_view(), name='api_learningcircles'),
    re_path(r'^learningcircles/successes/$', views.FinalReportListView.as_view(), name='api_learningcircles_successes'),
    re_path(r'^learningcircles/topics/$', views.LearningCircleTopicListView.as_view(), name='api_learningcircle_topics'),
    re_path(r'^learningcircles/cities/$', views.cities, name='api_learningcircles_cities'),
    re_path(r'^courses/$', views.CourseListView.as_view(), name='api_courses'),
    re_path(r'^courses/topics/$', views.CourseTopicListView.as_view(), name='api_course_topics'),
    re_path(r'^courses/languages/$', views.CourseLanguageListView.as_view(), name='api_course_languages'),
    re_path(r'^signup/$', views.SignupView.as_view(), name='api_learningcircles_signup'),
    re_path(r'^rsvp/$', views.MeetingRsvpView.as_view(), name='api_meeting_rsvp'),
    re_path(r'^learning-circle/$', views.LearningCircleCreateView.as_view(), name='api_learningcircles_create'),
    re_path(r'^learning-circle/(?P<study_group_id>[\d]+)/$', views.LearningCircleUpdateView.as_view(), name='api_learningcircles_update'),
    re_path(r'^upload_image/$', views.ImageUploadView.as_view(), name='api_image_upload'),
    re_path(r'^learning-circles-map/$', views.LearningCirclesMapView.as_view(), name='api_learningcircles_map'),
    re_path(r'^instagram-feed/$', views.InstagramFeed.as_view(), name='api_instagram_feed'),
    re_path(r'^teams/$', views.TeamListView.as_view(), name='api_teams'),
    re_path(r'^teams/(?P<team_id>[\d]+)/$', views.TeamDetailView.as_view(), name='api_teams_detail'),
    re_path(r'^teams/(?P<team_id>[\d]+)/invitation-url/create/$', views.create_team_invitation_link, name='api_teams_create_invitation_url'),
    re_path(r'^teams/(?P<team_id>[\d]+)/invitation-url/delete/$', views.delete_team_invitation_link, name='api_teams_delete_invitation_link'),
    re_path(r'^teams/members/$', views.TeamMembershipListView.as_view(), name='api_team_memberships'),
    re_path(r'^teams/invitations/$', views.TeamInvitationListView.as_view(), name='api_team_invitations'),
    re_path(r'^facilitator/invitations/$', views.facilitator_invitation_notifications, name='api_facilitator_invitations'),
    re_path(r'^announcements/$', views.AnnouncementListView.as_view(), name='api_announcements'),
    re_path(r'^drf/', include(router.urls)),
]
