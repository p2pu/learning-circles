# coding: utf-8
from django.conf import settings
from django.test import TestCase, override_settings
from django.test import Client

from studygroups.models import Announcement

import json

class TestAnnouncementsApi(TestCase):

    fixtures = ['test_announcements.json']

    def test_list_announcements(self):
        c = Client()
        response = c.get('/api/announcements/')
        self.assertEqual(response.status_code, 200)

        res_data = response.json()
        announcement = res_data["items"][0]

        expected_announcement = {
          "text": "Exploring virtual solutions for learning circles during quarantine? The P2PU community created a handbook to offer insight and support as you move your programs online.",
          "link": "https://www.p2pu.org/virtual-handbook",
          "link_text": "View handbook",
          "color": "yellow"
        }

        self.assertEqual(res_data["count"], 1)
        self.assertEqual(announcement, expected_announcement)

