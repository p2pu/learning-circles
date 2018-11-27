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
from .tasks import send_announcement

from freezegun import freeze_time

import datetime
import time
import hashlib
import hmac


class TestAnnounceViews(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']
    MESSAGE_DATA = {
        'recipient': 'announce@localhost', 
        'sender': 'Staff member <admin@example.net>',
        'from': 'Staff member <admin@example.net>',
        'subject': 'Monthly community update',
        'body-plain': 'This was the plain message',
        'body-html': '<html><body><h1>Hello</h1></body></html>',
        'timestamp': 123,
        'token': '123',
        'signature': '123',
    }


    def setUp(self):
        # create staff user
        user = User.objects.create_user('admin', 'admin@example.net', 'password')
        user.is_superuser = True
        user.is_staff = True
        user.save()
        # create 3 non staff
        create_user('user1@example.net', 'user', 'One', '123', True)
        create_user('user2@example.net', 'user', 'Two', '123', False)
        create_user('user3@example.net', 'user', 'Three', '123', True)

    
    @patch('announce.views.send_announcement')
    def test_webhook_signature_check(self, send_announcement):
        c = Client()
        resp = c.post('/announce/send/', self.MESSAGE_DATA)
        self.assertEqual(resp.status_code, 401)

        timestamp = time.time()
        token = '123456789'
        message_data = self.MESSAGE_DATA.copy()
        message_data['timestamp'] = timestamp
        message_data['token'] = token
        message_data['signature'] = hmac_digest = hmac.new(
            key=bytes(settings.MAILGUN_API_KEY, 'latin-1'),
            msg=bytes('{}{}'.format(timestamp, token), 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest()
        resp = c.post('/announce/send/', message_data)
        self.assertEqual(resp.status_code, 200)


    @patch('announce.views.send_announcement')
    def test_send_announcement_from_non_staff(self, send_announcement):
        c = Client()
        timestamp = time.time()
        token = '123456789'
        message_data = self.MESSAGE_DATA.copy()
        message_data['from'] = 'bob@foo.com'
        message_data['sender'] = 'bob@foo.com'
        message_data['timestamp'] = timestamp
        message_data['token'] = token
        message_data['signature'] = hmac_digest = hmac.new(
            key=bytes(settings.MAILGUN_API_KEY, 'latin-1'),
            msg=bytes('{}{}'.format(timestamp, token), 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest()
        resp = c.post('/announce/send/', message_data)
        self.assertEqual(resp.status_code, 406)
        self.assertFalse(send_announcement.delay.called)


    @patch('announce.views.send_announcement')
    def test_send_announcement(self, send_announcement):
        c = Client()
        timestamp = time.time()
        token = '123456789'
        message_data = self.MESSAGE_DATA.copy()
        message_data['timestamp'] = timestamp
        message_data['token'] = token
        message_data['signature'] = hmac_digest = hmac.new(
            key=bytes(settings.MAILGUN_API_KEY, 'latin-1'),
            msg=bytes('{}{}'.format(timestamp, token), 'latin-1'),
            digestmod=hashlib.sha256
        ).hexdigest()
        resp = c.post('/announce/send/', message_data)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(send_announcement.delay.called)


    @patch('announce.tasks.requests')
    def test_send_announcement_task(self, requests):
        requests.post = MagicMock()
        requests.post.return_value.status_code = 200
        send_announcement('Tester <test@example.net>', 'Subject', 'This is a message', '<html><body><h1>HTML message</h1></body></html>')
        self.assertTrue(requests.post.called)

        account_settings_url = ''.join([settings.DOMAIN, reverse('account_settings')])
        post_data = requests.post.call_args[1].get('data')
        self.assertEquals('text', post_data[2][0])
        self.assertIn(account_settings_url, post_data[2][1])
        self.assertEquals('html', post_data[3][0])
        self.assertIn(account_settings_url, post_data[3][1])

