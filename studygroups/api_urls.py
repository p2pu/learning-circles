from django.conf.urls import url
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

# TODO split / indicate what is used on www.p2pu.org vs what is used for management UX

urlpatterns = [
    url(r'^learningcircles/$', views.LearningCircleListView.as_view(), name='api_learningcircles'),
    url(r'^learningcircles/successes/$', views.FinalReportListView.as_view(), name='api_learningcircles_successes'),
    url(r'^learningcircles/topics/$', views.LearningCircleTopicListView.as_view(), name='api_learningcircle_topics'),
    url(r'^learningcircles/cities/$', views.cities, name='api_learningcircles_cities'),
    url(r'^courses/$', views.CourseListView.as_view(), name='api_courses'),
    url(r'^courses/topics/$', views.CourseTopicListView.as_view(), name='api_course_topics'),
    url(r'^courses/languages/$', views.CourseLanguageListView.as_view(), name='api_course_languages'),
    url(r'^signup/$', views.SignupView.as_view(), name='api_learningcircles_signup'),
    url(r'^rsvp/$', views.MeetingRsvpView.as_view(), name='api_meeting_rsvp'),
    url(r'^learning-circle/$', views.LearningCircleCreateView.as_view(), name='api_learningcircles_create'),
    url(r'^learning-circle/(?P<study_group_id>[\d]+)/$', views.LearningCircleUpdateView.as_view(), name='api_learningcircles_update'),
    url(r'^upload_image/$', views.ImageUploadView.as_view(), name='api_image_upload'),
    url(r'^learning-circles-map/$', views.LearningCirclesMapView.as_view(), name='api_learningcircles_map'),
    url(r'^instagram-feed/$', views.InstagramFeed.as_view(), name='api_instagram_feed'),
    url(r'^teams/$', views.TeamListView.as_view(), name='api_teams'),
    url(r'^teams/(?P<team_id>[\d]+)/$', views.TeamDetailView.as_view(), name='api_teams_detail'),
    url(r'^teams/(?P<team_id>[\d]+)/invitation-url/create/$', views.create_team_invitation_link, name='api_teams_create_invitation_url'),
    url(r'^teams/(?P<team_id>[\d]+)/invitation-url/delete/$', views.delete_team_invitation_link, name='api_teams_delete_invitation_link'),
    url(r'^teams/members/$', views.TeamMembershipListView.as_view(), name='api_team_memberships'),
    url(r'^teams/invitations/$', views.TeamInvitationListView.as_view(), name='api_team_invitations'),
    url(r'^facilitator/invitations/$', views.facilitator_invitation_notifications, name='api_facilitator_invitations'),
    url(r'^announcements/$', views.AnnouncementListView.as_view(), name='api_announcements'),
    url(r'^drf/', include(router.urls)),
]
