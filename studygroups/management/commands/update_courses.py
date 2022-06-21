from django.core.management.base import BaseCommand, CommandError

from studygroups.models import Course
import requests

class Command(BaseCommand):
    help = 'Fetch course updates from remote URL and apply them'

    def handle(self, *args, **options):
        UPDATE_URL = 'https://raw.githubusercontent.com/p2pu/learning-circles/course-updates/course-updates.json'
        resp = requests.get(UPDATE_URL)
        data = resp.json()
        for update in data.get('updates'):
            print(update)
            Course.objects.filter(pk=update['id']).update(**update)


