from django.urls import reverse
from django.utils import timezone
from django.db.models import OuterRef, Subquery, Q, Count, IntegerField
from django.conf import settings
from django.utils.text import slugify

from rest_framework import generics
from rest_framework import serializers, viewsets
from rest_framework import mixins
from rest_framework import permissions

from studygroups.models import Feedback
from studygroups.models import StudyGroup
from studygroups.models import TeamMembership
from studygroups.models import TeamInvitation
from studygroups.models import Meeting
from studygroups.models import get_study_group_organizers


class FeedbackSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse('feedback-detail', args=[obj.pk])

    class Meta:
        model = Feedback
        fields = ['rating', 'attendance', 'reflection', 'study_group_meeting', 'url']


class IsGroupFacilitator(permissions.BasePermission):

    def check_permission(self, user, study_group):
        if user.is_staff or user == study_group.facilitator \
                or TeamMembership.objects.active().filter(user=user, role=TeamMembership.ORGANIZER).exists() and user in get_study_group_organizers(study_group):
            return True
        return False

    
    def has_permission(self, request, view):
        meeting_id = request.data.get('study_group_meeting')
        meeting = Meeting.objects.get(pk=meeting_id)
        return self.check_permission(request.user, meeting.study_group)


    def has_object_permission(self, request, view, obj):
        """ give access to staff, user and team organizer """
        study_group = obj.study_group_meeting.study_group
        if request.user.is_staff \
                or request.user == study_group.facilitator \
                or TeamMembership.objects.active().filter(user=request.user, role=TeamMembership.ORGANIZER).exists() and request.user in get_study_group_organizers(study_group):
            return True
        return False


class FeedbackViewSet(
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupFacilitator]


""" TODO this is a duplicate since the way of getting the study_group differs :( """
class IsGroupFacilitatorII(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """ give access to staff, user and team organizer """
        study_group = obj
        if request.user.is_staff \
                or request.user == study_group.facilitator \
                or TeamMembership.objects.active().filter(user=request.user, role=TeamMembership.ORGANIZER).exists() and request.user in get_study_group_organizers(study_group):
            return True
        return False


class StudyGroupFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyGroup
        fields = ['facilitator_goal_rating', 'course_rating', 'course_rating_reason']


class StudyGroupRatingViewSet(
        mixins.UpdateModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupFacilitatorII]


class IsATeamOrganizer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """ give access to staff, user and team organizer """
        study_group = obj
        if request.user.is_staff \
                or request.user == study_group.facilitator \
                or TeamMembership.objects.active().filter(user=request.user, role=TeamMembership.ORGANIZER).exists():
            return True
        return False


class TeamInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInvitation
        fields = ['pk', 'created_at', 'email', 'role', 'responded_at', 'joined']


class TeamInvitationViewSet(
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    serializer_class = TeamInvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsATeamOrganizer]

    def get_queryset(self):
        team_membership = TeamMembership.objects.active().filter(user=self.request.user, role=TeamMembership.ORGANIZER).get()
        return TeamInvitation.objects.filter(team=team_membership.team, responded_at__isnull=True)


class TeamMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMembership
        fields = ['pk', 'user', 'role', 'weekly_update_opt_in', 'created_at']


class TeamMembershipViewSet(
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    serializer_class = TeamMembershipSerializer
    permission_classes = [permissions.IsAuthenticated, IsATeamOrganizer]

    def get_queryset(self):
        team_membership = TeamMembership.objects.active().filter(user=self.request.user, role=TeamMembership.ORGANIZER).get()
        return TeamMembership.objects.active().filter(team=team_membership.team)



class MemberLearningCircleSerializer(serializers.ModelSerializer):

    next_meeting_date = serializers.DateField()
    user_signup = serializers.IntegerField()
    signup_url = serializers.SerializerMethodField()

    def signup_url(self, obj):
        return f"{settings.PROTOCOL}://{settings.DOMAIN}" + reverse('studygroups_signup', args=(slugify(obj.venue_name, allow_unicode=True), obj.id))

    class Meta:
        model = StudyGroup
        fields = ['id', 'name', 'next_meeting_date', 'user_signup', 'signup_url']


class IsMemberTeamMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        """ give access to staff, user and team organizer """
        if request.user.is_staff \
            or TeamMembership.objects.active().filter(user=request.user, team__membership=True).exists():
            return True
        return False


class MemberLearningCircleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    serializer_class = MemberLearningCircleSerializer
    permission_classes = [permissions.IsAuthenticated, IsMemberTeamMember]

    def get_queryset(self):
        today = timezone.now().date()
        study_groups = StudyGroup.objects.published().prefetch_related('course', 'meeting_set', 'application_set').order_by('id')
        upcoming_meetings = Meeting.objects.filter(
            study_group=OuterRef('pk'), 
            deleted_at__isnull=True,
            meeting_date__gte=today
        ).order_by('meeting_date')
        study_groups = study_groups\
            .filter(unlisted=True)\
            .annotate(next_meeting_date=Subquery(upcoming_meetings.values('meeting_date')[:1]))\
            .annotate(
                user_signup=Count(
                    'application', 
                    filter=Q(application__email__iexact=self.request.user.email)
                )
            )\
            .filter(Q(end_date__gte=today) | Q(draft=True))
        return study_groups

