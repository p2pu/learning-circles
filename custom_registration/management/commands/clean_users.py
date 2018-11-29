from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Clean up users in the database'

    def handle(self, *args, **options):
        # Delete all users who haven't logged in 
        users_for_deletion = User.objects.filter(
            last_login=None, 
            profile__communication_opt_in=False,
            date_joined__lt = timezone.now() - datetime.timedelta(weeks=2)
        )
        print('{} users cleaned up'.format(users_for_deletion.count()))
        users_for_deletion.delete()
