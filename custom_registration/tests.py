# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User

import re
import json


"""
Tests for when facilitators interact with the system
"""
class TestCustomRegistrationViews(TestCase):

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
        url = '/en/accounts/register/'
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


    def test_email_address_confirm(self):
        c = Client()
        url = '/en/accounts/register/'
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


