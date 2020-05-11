# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.conf import settings
from django.core import mail
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.translation import get_language
from django.urls import reverse

from mock import patch, MagicMock

from custom_registration.models import create_user

from freezegun import freeze_time

import datetime


class TestCommunityCalendar(TestCase):

    fixtures = ['test_events.json']

    def setUp(self):
        # create staff user
        user = create_user('admin@example.net', 'admin', 'bob', 'password')
        user.is_superuser = True
        user.is_staff = True
        user.save()
        # create 3 non staff
        create_user('user1@example.net', 'user', 'One', '123', True)
        create_user('user2@example.net', 'user', 'Two', '123', False)
        create_user('user3@example.net', 'user', 'Three', '123', True)

    def test_public_api(self):
        pass
