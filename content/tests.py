from django.test import Client
from django.test import TestCase

from custom_registration.models import create_user
from content import models as content_model


class CourseTests(TestCase):

    test_username = 'testuser'
    test_email = 'test@mail.org'
    test_password = 'testpass'

    test_username2 = 'bob'
    test_email2 = 'bob@mail.org'
    test_password2 = '13245'

    def setUp(self):
        self.client = Client()
        self.locale = 'en'

        self.user = create_user(
            self.test_email,
            self.test_username,
            'lastname',
            self.test_password
        )
        
        self.user2 = create_user(
            self.test_email2,
            self.test_username2,
            'lastname2',
            self.test_password2
        )


    def test_content_creation(self):
        content = content_model.create_content('title', 'content', '/uri/users/bob')
        content = content_model.get_content(content['uri'])
        self.assertEquals(content, content)


    def test_content_history(self):
        content = content_model.create_content('title', 'content', '/uri/users/bob')
        content_model.update_content(
            content['uri'], 'New title', 'New content', '/uri/users/testuser'
        )
        # TODO this doesn't test anything?


    def test_clone_content(self):
        content = content_model.create_content('title', 'content', '/uri/users/bob')
        clone = content_model.clone_content(content['uri'])
        for key in ['title', 'content']:
            self.assertTrue(content[key], clone[key])
