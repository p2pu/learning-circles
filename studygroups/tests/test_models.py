from django.test import TestCase
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User

from mock import patch

from studygroups.models import StudyGroup
from studygroups.models import StudyGroupSignup
from studygroups.models import Application
from studygroups.models import accept_application

# Create your tests here.
class TestSignupModels(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json']

    APPLICATION_DATA = {
        'name': 'Test User',
        'contact_method': 'Email',
        'email': 'test@mail.com',
        'computer_access': 'Yes', 
        'goals': 'try hard',
        'support': 'thinking how to?',
        'study_groups': '1',
    }


    def setUp(self):
        user = User.objects.create_user('admin', 'admin@test.com', 'password')


    @patch('studygroups.views.send_message')
    def test_accept_application(self, send_message):
        self.assertEqual(StudyGroupSignup.objects.all().count(),0)
        data = self.APPLICATION_DATA
        del data['study_groups']
        application = Application(**data)
        application.save()
        application.study_groups.add(StudyGroup.objects.all()[0])
        accept_application(application)
        self.assertEqual(StudyGroupSignup.objects.all().count(),1)


