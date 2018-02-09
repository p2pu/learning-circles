# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User

from .models import create_user

from mock import patch

import re
import json

from studygroups.models import Facilitator


"""
Tests for when facilitators interact with the system
"""
class TestCustomRegistrationViews(TestCase):

    @patch('custom_registration.signals.add_member_to_list')
    def test_account_create(self, add_member_to_list):
        c = Client()
        data = {
            "email": "test@example.net",
            "first_name": "firstname",
            "last_name": "lastname",
            "newsletter": "on",
            "password1": "password",
            "password2": "password",
        }
        resp = c.post('/en/accounts/register/', data)
        self.assertRedirects(resp, '/en/facilitator/')
        users = User.objects.filter(email__iexact=data['email'])
        self.assertEquals(users.count(), 1)
        facilitator = Facilitator.objects.get(user=users.first())
        self.assertEquals(facilitator.mailing_list_signup, True)
        self.assertTrue(add_member_to_list.called)
        self.assertEquals(len(mail.outbox), 1) ##
        self.assertIn('Please confirm your email address', mail.outbox[0].subject)


    @patch('custom_registration.signals.add_member_to_list')
    def test_facilitator_signup_with_mixed_case(self, add_member_to_list):
        c = Client()
        data = {
            "email": "ThIsNoTaGoOd@EmAil.CoM",
            "first_name": "firstname",
            "last_name": "lastname",
            "password1": "password",
            "password2": "password",
        }
        resp = c.post('/en/accounts/register/', data)
        self.assertRedirects(resp, '/en/facilitator/')
        data['email'] = data['email'].upper()
        resp = c.post('/en/accounts/register/', data)
        users = User.objects.filter(username__iexact=data['email'])
        self.assertEquals(users.count(), 1)
        facilitator = Facilitator.objects.get(user=users.first())
        self.assertFalse(facilitator.mailing_list_signup)
        self.assertFalse(add_member_to_list.called)
        self.assertEquals(len(mail.outbox), 1)
        self.assertIn('Please confirm your email', mail.outbox[0].subject)


    def test_login_redirect(self):
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
        c = Client()
        c.login(username='bob123', password='password')
        resp = c.get('/en/accounts/login/', follow=True)
        self.assertEquals(resp.redirect_chain, [
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
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to[0], 'bob@example.net')

        mail.outbox = []
        resp = c.post('/en/accounts/password_reset/', {
            'email': 'BOB@example.net'
        })
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to[0], 'BOB@example.net')


    # Test /reset/uuidb64/token/ to verify url and test automatic login
    def test_password_reset_complete(self):
        user = User.objects.create_user('bob123', 'bob@example.net', 'password')
        c = Client()
        resp = c.post('/en/accounts/password_reset/', {
            'email': 'bob@example.net'
        })
        self.assertEquals(len(mail.outbox), 1)

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
            "newsletter": False
        }
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), 
            {"status": "created", "user": data['email']}
        )
        bob = User.objects.get(email=data['email'])
        self.assertEqual(bob.first_name, 'Bob')
        self.assertEqual(bob.facilitator.mailing_list_signup, False)
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
        self.assertEquals(bob.facilitator.email_confirmed_at, None)


    def test_email_address_confirm(self):
        c = Client()
        url = '/en/accounts/fe/register/'
        data = {
            "email": "bobtest@mail.com",
            "first_name": "Bob",
            "last_name": "Test",
            "password": "12345",
            "newsletter": False
        }
        resp = c.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), 
            {"status": "created", "user": data['email']}
        )
        self.assertEqual(len(mail.outbox), 1)
        bob = User.objects.get(email=data['email'])
        self.assertEquals(bob.facilitator.email_confirmed_at, None)

        # get email confirmation URL
        match = re.search(r'/en/accounts/email_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', mail.outbox[0].body)
        confirm_url = match.group(0)
        c.logout()
        res = c.get(confirm_url)
        self.assertRedirects(res, '/en/facilitator/')
        bob = User.objects.get(email=data['email'])
        self.assertNotEquals(bob.facilitator.email_confirmed_at, None)


