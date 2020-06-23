from django.core.management.base import BaseCommand, CommandError

from studygroups.discourse import remove_empty_discourse_links

class Command(BaseCommand):
    help = 'Remove discourse links for courses with no discussion'

    def handle(self, *args, **options):
        remove_empty_discourse_links()
