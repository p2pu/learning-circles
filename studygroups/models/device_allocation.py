# coding=utf-8
from django.contrib.auth.models import User

from django.db import models

from studygroups.models import Facilitator
from studygroups.models import StudyGroup
import logging

logger = logging.getLogger(__name__)


# NOTE: the current method is probably not suited to manage multiple overlapping device allocations. That is most likely fine for the current use case. But if the use case is expanded in the future, requirements should be clearly defined and the implementation should be adapted accordingly


class DeviceAllocation(models.Model):
    """ date range applies to start date """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    cutoff_date = models.DateField()
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user.first_name} - {self.amount} device(s)'


def check_user_device_allocation(user, date):
    """ check number of devices available to a facilitator """

    device_allocations = DeviceAllocation.objects.filter(
        user=user,
        start_date__lte=date,
        cutoff_date__gte=date
    )

    if device_allocations.count() == 0:
        logger.warning('No active DeviceAllocation for user')
        return 0

    if device_allocations.count() > 1:
        logger.warning('Multiple overlapping DeviceAllocations for user')

    # should just be one device allocation
    device_allocation = device_allocations.first()

    # Find any learning circles in the device allocation time period
    study_groups = StudyGroup.objects.active().filter(
        facilitator__user=user,
        start_date__gte=device_allocation.start_date,
        start_date__lt=device_allocation.cutoff_date,
    )

    used_allocation = sum(
        filter(lambda x: x is not None, [lc.signup_limit for lc in study_groups])
    )

    return max(device_allocation.amount - used_allocation, 0)
