# coding=utf-8
from django.contrib.auth.models import User

from django.db import models

from studygroups.models import Facilitator
from studygroups.models import StudyGroup


# NOTE: the current method is probably not suited to manage multiple overlapping device allocations. That is most likely fine for the current use case. But if the use case is expanded in the future, requirements should be clearly defined and the implementation should be adapted accordingly


class DeviceAllocation(models.Model):
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
    # TODO assert that only one allocation is active for a date period?
    allocated_amount = sum([da.amount for da in device_allocations])

    # Get min of start_date for device allocations
    first_date = min([da.start_date for da in device_allocations])
    # Get max of cutoff_date for device allocations
    cutoff_date = max([da.cutoff_date for da in device_allocations])

    # Find any learning circles in the device allocation time period
    study_groups = StudyGroup.objects.active().filter(
        facilitator__user=user,
        start_date__gte=first_date,
        end_date__lt=cutoff_date,
    )

    used_allocation = sum(
        filter(lambda x: x is not None, [lc.signup_limit for lc in study_groups])
    )

    return max(allocated_amount - used_allocation, 0)


def devices_available(learning_circle):
    """ check maximum number of devices available for learning circle """
   
    facilitator_user_ids = learning_circle.facilitator_set.all().values_list('user_id')
    study_group_ids = Facilitator.objects.all().filter(user_id__in=facilitator_user_ids).values_list('study_group_id')

    device_allocations = DeviceAllocation.objects.filter(
        user_id__in=facilitator_user_ids,
        start_date__lte=learning_circle.start_date,
        cutoff_date__gte=learning_circle.start_date
    )

    # Get min of start_date for device allocations
    first_date = min([da.start_date for da in device_allocations])
    # Get max of cutoff_date for device allocations
    cutoff_date = max([da.cutoff_date for da in device_allocations])

    amount = sum([da.amount for da in device_allocations])

    other_lcs = StudyGroup.objects.active().filter(
        pk__in=study_group_ids,
        start_date__gte=first_date,
        end_date__lt=cutoff_date,
    )
    other_lcs = other_lcs.exclude(pk=learning_circle.pk)

    # count limits for other learning circles
    # TODO ensure there are no unlimted signups for other learning circles!
    total = sum(filter(lambda x: x, [lc.signup_limit for lc in other_lcs]))
    if amount > total:
        return amount-total
    return 0
