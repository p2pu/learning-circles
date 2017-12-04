# coding: utf-8
from django.test import TestCase, override_settings
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User

import re


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
