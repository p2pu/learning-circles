from django.test import LiveServerTestCase, override_settings, tag, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from django.utils import timezone

from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from studygroups.models import Course
from studygroups.models import StudyGroup
from studygroups.models import Meeting
from custom_registration.models import create_user

from datetime import timedelta, time

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
        meeting_date = timezone.now() - timedelta(days=2)
        meeting = Meeting.objects.create(study_group=sg, meeting_date=meeting_date.date(), meeting_time=time(18, 0))

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

        # Make sure meeting feedback component is loaded
        meeting = self.study_group.meeting_set.first()
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.ID, f'meeting-{meeting.pk}-feedback'),
        ))

        # Make sure learning circle feedback is present
        # learning-circle-feedback .meeting-item
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '#learning-circle-feedback .meeting-item'),
        ))


    def test_meeting_feedback(self):
        self.driver.get(f'{self.live_server_url}/en/studygroup/{self.study_group.pk}/')
        self.assertTrue(expected_conditions.title_is('P2PU Learning Circles'))
        self.assertTrue(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, 'h1'),
                self.study_group.name
            )
        )

        # Make sure meeting feedback component is loaded
        meeting = self.study_group.meeting_set.first()
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.ID, f'meeting-{meeting.pk}-feedback'),
        ))

        collapse = self.wait.until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '#meeting-1 > div:nth-child(2) > a:nth-child(1)'))
        )
        collapse.click()

        self.assertEqual(meeting.feedback_set.count(), 0)

        attendance = self.driver.find_element_by_id("id_attendance")
        actions = ActionChains(self.driver)
        actions.move_to_element(attendance).perform()
        attendance.send_keys('3')

        #pw_bot = self.wait.until(
        #    expected_conditions.element_to_be_clickable(
        #        (By.CSS_SELECTOR, ".p2pu-bot-selector > label:nth-child(1) > input:nth-child(1)")
        #    )
        #)
        #pw_bot.click()

        self.wait.until(
            expected_conditions.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    'div.text-muted:nth-child(3)'
                ),
                'changes saved'
            )
        )
        self.assertEquals(meeting.feedback_set.count(), 1)
        self.assertEquals(meeting.feedback_set.first().attendance, 3)


    def test_learning_circle_rating(self):
        StudyGroup.objects.filter(pk=1).update(facilitator_goal='to test things')
        self.driver.get(f'{self.live_server_url}/en/studygroup/{self.study_group.pk}/')
        self.assertTrue(expected_conditions.title_is('P2PU Learning Circles'))

        # Make sure learning circle feedback is present
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '#learning-circle-feedback .meeting-item'),
        ))

        self.assertEquals(StudyGroup.objects.get(pk=1).facilitator_goal_rating, None)
        rating_feedback = self.driver.find_element_by_css_selector(
            "div.star-rating-input:nth-child(3) > label:nth-child(3) > svg:nth-child(2)"
        )
        actions = ActionChains(self.driver)
        actions.move_to_element(rating_feedback).perform()
        actions.click(rating_feedback)
        actions.perform()

        self.wait.until(
            expected_conditions.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "div.text-muted:nth-child(2)"
                ),
                'changes saved'
            )
        )
        self.assertEquals(StudyGroup.objects.get(pk=1).facilitator_goal_rating, 3)
    

    def test_course_rating(self):
        StudyGroup.objects.filter(pk=1).update(facilitator_goal='to test things')
        self.driver.get(f'{self.live_server_url}/en/studygroup/{self.study_group.pk}/')
        self.assertTrue(expected_conditions.title_is('P2PU Learning Circles'))

        # Make sure learning circle feedback is present
        self.wait.until(expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, '#learning-circle-feedback .meeting-item'),
        ))
        
        self.assertEquals(StudyGroup.objects.get(pk=1).course_rating, None)
        course_rating = self.driver.find_element_by_css_selector(
            "div.star-rating-input:nth-child(2) > label:nth-child(4) > svg:nth-child(2)"
        )
        actions = ActionChains(self.driver)
        actions.move_to_element(course_rating).perform()
        actions.click(course_rating)
        actions.perform()

        self.wait.until(
            expected_conditions.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "div.text-muted:nth-child(2)"
                ),
                'changes saved'
            )
        )
        self.assertEquals(StudyGroup.objects.get(pk=1).course_rating, 4)

