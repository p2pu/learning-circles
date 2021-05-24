from django.urls import reverse

from rest_framework import generics
from rest_framework import serializers, viewsets
from rest_framework import mixins
from rest_framework import permissions

from studygroups.models import Feedback
from studygroups.models import TeamMembership
from studygroups.models import get_study_group_organizers



class FeedbackSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse('feedback-detail', args=[obj.pk])

    class Meta:
        model = Feedback
        fields = ['rating', 'attendance', 'reflection', 'study_group_meeting', 'url']


class IsGroupFacilitator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """ give access to staff, user and team organizer """
        study_group = obj.study_group_meeting.study_group
        if request.user.is_staff \
                or request.user == study_group.facilitator \
                or TeamMembership.objects.active().filter(user=request.user, role=TeamMembership.ORGANIZER).exists() and request.user in get_study_group_organizers(study_group):
            return True
        return False


class FeedbackViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupFacilitator]
