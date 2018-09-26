# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User
from django.utils.timezone import utc

from mock import patch
from freezegun import freeze_time

import re
import json
import datetime

from studygroups.models import Profile
from .models import create_user
from .tasks import send_new_user_emails


"""
Tests for when facilitators interact with the system
"""
class TestCustomRegistrationViews(TestCase):

    def test_account_create(self):
        c = Client()
        data = {
            "email": "test@example.net",
            "first_name": "firstname",
            "last_name": "lastname",
            "communication_opt_in": "on",
            "interested_in_learning": "python",
            "password1": "password",
            "password2": "password",
        }
        resp = c.post('/en/accounts/register/', data)
        self.assertRedirects(resp, '/en/facilitator/')
        users = User.objects.filter(email__iexact=data['email'])
        self.assertEqual(users.count(), 1)
        profile = Profile.objects.get(user=users.first())
        self.assertEqual(profile.interested_in_learning, "python")
        self.assertEqual(profile.communication_opt_in, True)
        self.assertEqual(len(mail.outbox), 1) ##
        self.assertIn('Please confirm your email address', mail.outbox[0].subject)


    def test_facilitator_signup_with_mixed_case(self):
        c = Client()
        data = {
            "email": "ThIsNoTaGoOd@EmAil.CoM",
            "first_name": "firstname",
            "last_name": "lastname",
            "password1": "password",
            "password2": "password",
            "communication_opt_in": "on",
        }
        resp = c.post('/en/accounts/register/', data)
        self.assertRedirects(resp, '/en/facilitator/')
        data['email'] = data['email'].upper()
        resp = c.post('/en/accounts/register/', data)
        users = User.objects.filter(username__iexact=data['email'])
        self.assertEqual(users.count(), 1)
        profile = Profile.objects.get(user=users.first())
        self.assertTrue(profile.communication_opt_in)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Please confirm your email', mail.outbox[0].subject)


    def test_login_redirect(self):
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
        c = Client()
        c.login(username='bob123', password='password')
        resp = c.get('/en/accounts/login/', follow=True)
        self.assertEqual(resp.redirect_chain, [
            ('/login_redirect/', 302),
            ('/en/login_redirect/', 302),
            ('/en/facilitator/', 302)
        ])


    # Test /accounts/password_reset/ for correct handling of case
    def test_password_reset_submit(self):
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
        c = Client()
        resp = c.post('/en/accounts/password_reset/', {
            'email': 'bob@example.net'
        })
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], 'bob@example.net')

        mail.outbox = []
        resp = c.post('/en/accounts/password_reset/', {
            'email': 'BOB@example.net'
        })
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], 'BOB@example.net')


    # Test /reset/uuidb64/token/ to verify url and test automatic login
    def test_password_reset_complete(self):
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
        c = Client()
        resp = c.post('/en/accounts/password_reset/', {
            'email': 'bob@example.net'
        })
        self.assertEqual(len(mail.outbox), 1)

        match = re.search(r'/en/accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', mail.outbox[0].body)
        reset_url = match.group(0)
        set_password_url = '/en/accounts/reset/{}/set-password/'.format(match.group(1))
        res = c.get(reset_url)
        self.assertRedirects(res, set_password_url)

        res = c.post(set_password_url, {
            'new_password1': 'newpass',
            'new_password2': 'newpass'
        }, follow=True)
        self.assertRedirects(res, '/en/facilitator/')


    def test_api_account_create(self):
        c = Client()
        url = '/en/accounts/fe/register/'
        data = {
            "email": "bobtest@mail.com",
            "first_name": "Bob",
            "last_name": "Test",
            "password": "12345",
            "communication_opt_in": False
        }
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(),
            {"status": "created", "user": data['email']}
        )
        bob = User.objects.get(email=data['email'])
        self.assertEqual(bob.first_name, 'Bob')
        self.assertEqual(bob.profile.communication_opt_in, False)
        # make sure email confirmation email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(data['email'], mail.outbox[0].to)
        self.assertEqual(mail.outbox[0].subject, 'Please confirm your email address')


    @patch('custom_registration.signals.send_email_confirm_email')
    def test_ajax_login(self, send_email_confirm_email):
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        c = Client()
        data = {
            "email": "bob@example.net",
            "password": "password",
        }
        url = '/en/accounts/fe/login/'
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(),
            {"status": "success", "user": data['email']}
        )


    @patch('custom_registration.signals.handle_new_facilitator')
    def test_email_address_confirm_request(self, handle_new_facilitator):
        user = create_user('bob@example.net', 'bob', 'test', 'password', False)
        c = Client()
        c.login(username='bob@example.net', password='password')

        mail.outbox = []
        resp = c.post('/en/accounts/email_confirm/')
        self.assertRedirects(resp, '/en/facilitator/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.email, mail.outbox[0].to)
        self.assertEqual(mail.outbox[0].subject, 'Please confirm your email address')
        bob = User.objects.get(email=user.email)
        self.assertEqual(bob.profile.email_confirmed_at, None)


    def test_email_address_confirm(self):
        c = Client()
        url = '/en/accounts/fe/register/'
        data = {
            "email": "bobtest@mail.com",
            "first_name": "Bob",
            "last_name": "Test",
            "password": "12345",
            "communication_opt_in": False
        }
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(),
            {"status": "created", "user": data['email']}
        )
        self.assertEqual(len(mail.outbox), 1)
        bob = User.objects.get(email=data['email'])
        self.assertEqual(bob.profile.email_confirmed_at, None)

        # get email confirmation URL
        match = re.search(r'/en/accounts/email_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', mail.outbox[0].body)
        confirm_url = match.group(0)
        c.logout()
        res = c.get(confirm_url)
        self.assertRedirects(res, '/en/facilitator/')
        bob = User.objects.get(email=data['email'])
        self.assertNotEqual(bob.profile.email_confirmed_at, None)
    

    def test_send_new_user_email(self):
        c = Client()
        data = {
            "email": "test@example.net",
            "first_name": "firstname",
            "last_name": "lastname",
            "communication_opt_in": "on",
            "password1": "password",
            "password2": "password",
        }
        resp = c.post('/en/accounts/register/', data)
        self.assertRedirects(resp, '/en/facilitator/')
        users = User.objects.filter(email__iexact=data['email'])
        self.assertEqual(users.count(), 1)
        profile = Profile.objects.get(user=users.first())
        profile.email_confirmed_at = datetime.datetime(2018, 9, 5, 12, 37, tzinfo=utc)
        profile.save()
        
        mail.outbox = []
        with freeze_time('2018-09-05 12:39:00'):
            send_new_user_emails()
        self.assertEqual(len(mail.outbox), 0)

        with freeze_time('2018-09-05 12:40:00'):
            send_new_user_emails()
        self.assertEqual(len(mail.outbox), 1)

        mail.outbox = []
        with freeze_time('2018-09-05 12:51:00'):
            send_new_user_emails()
        self.assertEqual(len(mail.outbox), 0)



