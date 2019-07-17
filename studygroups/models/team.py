from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.conf import settings
from django.urls import reverse

from .base import LifeTimeTrackingModel

import uuid

class Team(models.Model):
    name = models.CharField(max_length=128)
    page_slug = models.SlugField(max_length=256, blank=True)
    page_image = models.ImageField(blank=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    zoom = models.IntegerField(default=7)
    created_at = models.DateTimeField(auto_now_add=True)
    email_domain = models.CharField(max_length=128, blank=True)
    invitation_token = models.UUIDField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.name

    def generate_invitation_token(self):
        try:
            self.invitation_token = uuid.uuid4()
            self.save()
        except IntegrityError:
            generate_invitation_token(self)

    def team_invitation_url(self):
        if self.invitation_token is None:
            return None

        base_url = f'{settings.PROTOCOL}://{settings.DOMAIN}'
        path = reverse('studygroups_facilitator_invitation_confirm_token', kwargs={'token': self.invitation_token})

        return base_url + path


class TeamMembership(LifeTimeTrackingModel):
    ORGANIZER = 'ORGANIZER'
    MEMBER = 'MEMBER'
    ROLES = (
        (ORGANIZER, _('Organizer')),
        (MEMBER, _('Member')),
    )
    team = models.ForeignKey('studygroups.Team', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=256, choices=ROLES)
    weekly_update_opt_in = models.BooleanField(default=True)

    def __str__(self):
        return 'Team membership: {}'.format(self.user.__str__())


class TeamInvitation(models.Model):
    """ invittion for users to join a team """
    team = models.ForeignKey('studygroups.Team', on_delete=models.CASCADE)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE) # organizer who invited the user
    email = models.EmailField()
    role = models.CharField(max_length=256, choices=TeamMembership.ROLES)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    joined = models.NullBooleanField(null=True)

    def __str__(self):
        return 'Invitation <{} to join {}>'.format(self.email, self.team.name)


def get_study_group_organizers(study_group):
    """ Return the organizers for the study group """
    team_membership = TeamMembership.objects.active().filter(user=study_group.facilitator)
    if team_membership.count() == 1:
        organizers = team_membership.first().team.teammembership_set.active().filter(role=TeamMembership.ORGANIZER).values('user')
        return User.objects.filter(pk__in=organizers)
    return []


def get_team_users(user):
    """ Return the team members for a user """
    # TODO this function doesn't make sense - only applies for logged in users
    # change functionality or rename to get_team_mates
    team_membership = TeamMembership.objects.active().filter(user=user)
    if team_membership.count() == 1:
        members = team_membership.first().team.teammembership_set.active().values('user')
        return User.objects.filter(pk__in=members)
    return []


""" Return the team a user belongs to """
def get_user_team(user):
    team_membership = TeamMembership.objects.active().filter(user=user).get()
    return team_membership.team


def eligible_team_by_email_domain(user):
    # user is already on a team
    if TeamMembership.objects.active().filter(user=user).exists():
        return None

    email_domain = user.email.rsplit('@', 1)[1]
    matching_team = Team.objects.filter(email_domain=email_domain).first()

    # user already has an explicit invitation to this team or has already responsed to an invitation to this team
    if TeamInvitation.objects.filter(email=user.email, team=matching_team).exists():
        return None

    # team must have an organizer to create invitation
    if not TeamMembership.objects.active().filter(team=matching_team, role=TeamMembership.ORGANIZER).exists():
        return None

    return matching_team


