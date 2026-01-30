# coding=utf-8
from django.contrib.auth.models import User

from django.db import models

from studygroups.models import Facilitator
from studygroups.models import StudyGroup



# this is the model we use
class DeviceAllocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    cutoff_date = models.DateField()
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user.first_name} - {self.amount} device(s)'


def devices_available(learning_circle):
    facilitator_user_ids = learning_circle.facilitator_set.all().values_list('user_id')
    study_group_ids = Facilitator.objects.all().filter(user_id__in=facilitator_user_ids).values_list('study_group_id')

    device_allocations = DeviceAllocation.objects.filter(user_id__in=facilitator_user_ids)

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




