from django.test import TestCase
from django.test import Client

from mock import patch

from studygroups.models import Course
from studygroups.models import Application

# Create your tests here.
class TestSignupViews(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    SIGNUP_DATA = {
        'name': 'Test User',
        'contact_method': 'Email',
        'email': 'test@mail.com',
        'computer_access': 'Yes', 
        'goals': 'try hard',
        'support': 'thinking how to?',
        'study_groups': '1',
    }


    def setUp(self):
        pass


    def test_submit_application(self):
        c = Client()
        resp = c.post('/en/apply/', self.SIGNUP_DATA)
        print(resp)
        self.assertRedirects(resp, '/en/')
        self.assertEquals(Application.objects.all().count(), 1)


    def test_send_message(self):
        # Test sending a message
        pass

