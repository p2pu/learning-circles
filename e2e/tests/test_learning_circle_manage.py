from django.test import LiveServerTestCase, override_settings, tag, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from studygroups.models import Course
from studygroups.models import StudyGroup
from custom_registration.models import create_user, confirm_user_email
#from e2e.tests.selenium.page_objects import LearningCircleCreationPage
#from e2e.tests.selenium.locators import LearningCircleCreationPageLocators
#from e2e.tests.selenium.locators import RegistrationModalLocators

import socket

@override_settings(ALLOWED_HOSTS=['*'])
class LearningCircleManage(StaticLiveServerTestCase):
    fixtures = ['test_courses.json', 'test_studygroups.json']
    host = '0.0.0.0'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.host = socket.gethostbyname(socket.gethostname())
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-web-security')
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        #chrome_options.add_argument('--auto-open-devtools-for-tabs')
        #chrome_options.add_argument('--start-maximized')
        capabilities = DesiredCapabilities.CHROME
        capabilities['loggingPrefs'] = { 'browser':'ALL' }
        cls.driver = webdriver.Remote(
          command_executor='http://selenium:4444/wd/hub',
          desired_capabilities=capabilities,
          options=chrome_options
        )
        timeout = 10
        #cls.driver.implicitly_wait(timeout)
        cls.wait = WebDriverWait(cls.driver, timeout)


    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()


    def setUp(self):
        self.facilitator = create_user('hi@example.net', 'bowie', 'wowie', 'password')
        sg = StudyGroup.objects.get(pk=1)
        sg.facilitator = self.facilitator
        sg.save()
        self.study_group = sg

        client = Client()
        client.login(username=self.facilitator.username, password='password')
        cookie = client.cookies['sessionid']
        self.driver.get(self.live_server_url)
        self.driver.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.driver.refresh()


    def test_page(self):
        self.driver.get(f'{self.live_server_url}/en/studygroup/{self.study_group.pk}/')
        self.assertTrue(expected_conditions.title_is('P2PU Learning Circles'))
        self.assertTrue(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, 'h1'),
                self.study_group.name
            )
        )
        # Make sure react build is loaded


    def test_meeting_feedback(self):
        pass


    def test_learning_circle_rating(self):
        pass


    def test_course_rating(self):
        pass
