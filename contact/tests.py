# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language
from django.conf import settings

from unittest.mock import patch

from custom_registration.models import create_user

from freezegun import freeze_time

import datetime
import urllib.request, urllib.parse, urllib.error
import json

from .tasks import send_contact_form_inquiry

"""
Tests for when a learner interacts with the system. IOW:
    - signups
    - rsvps
"""

class TestContactApi(TestCase):

    def test_submit_contact_request(self):
        contact_data = {
            'email': 'bob@mail.com',
            'name': 'Bob',
            'content': 'blah blah blah',
            'source': '/contact/test',
        }
        send_contact_form_inquiry(**contact_data)
        # Make sure notification was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], settings.TEAM_EMAIL)
        self.assertEqual(mail.outbox[0].cc[0], settings.SUPPORT_EMAIL)
        self.assertIn(contact_data['content'], mail.outbox[0].body)
        self.assertIn(settings.SUPPORT_EMAIL, mail.outbox[0].reply_to)
        self.assertIn(contact_data['email'], mail.outbox[0].reply_to)

