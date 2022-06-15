from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class SoftDeleteQuerySet(models.QuerySet):

    def active(self):
        return self.filter(deleted_at__isnull=True)

    def delete(self, *args, **kwargs):
        # Stop bulk deletes
        self.update(deleted_at=timezone.now())
        #TODO: check if we need to set any flags on the query set after the delete


class LifeTimeTrackingModel(models.Model):
    """ Models that should be publicly deleted, but kept in the database """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteQuerySet.as_manager()

    def delete(self, *args, **kwargs):
        # Don't actually delete the object, affects django admin also
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    class Meta:
        abstract = True


class ModeratedQuerySet(models.QuerySet):

    def moderated(self):
        """ iow, moderated().active() or active().moderated() will get you stuff to show """
        return self.filter(moderated_at__isnull=False, moderation_approved=True)

    def to_moderate(self):
        return self.filter(moderated_at__isnull=True)


class Moderatable(models.Model):
    """ When moderating, deleted_at will be set to indicate spam """
    moderated_at = models.DateTimeField(blank=True, null=True)
    moderated_by = models.ForeignKey(User, blank=True, null=True, related_name='moderator', on_delete=models.SET_NULL)
    moderation_approved = models.BooleanField(blank=True, null=True)
    moderation_note = models.CharField(max_length=256, blank=True)

    objects = ModeratedQuerySet.as_manager()

    class Meta:
        abstract = True
