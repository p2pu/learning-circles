from django.test import LiveServerTestCase, override_settings, tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait

from studygroups.models import Course
from studygroups.models import StudyGroup
from custom_registration.models import create_user, confirm_user_email
from e2e.tests.selenium.page_objects import LearningCircleCreationPage
from e2e.tests.selenium.locators import LearningCircleCreationPageLocators
from e2e.tests.selenium.locators import RegistrationModalLocators

import socket

@override_settings(ALLOWED_HOSTS=['*'])
class LearningCircleCreation(StaticLiveServerTestCase):
    fixtures = ['test_courses.json']
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
        cls.driver = webdriver.Remote(
          command_executor='http://selenium:4444/wd/hub',
          desired_capabilities=DesiredCapabilities.CHROME,
          options=chrome_options
        )
        timeout = 20
        cls.driver.implicitly_wait(timeout)
        cls.wait = WebDriverWait(cls.driver, timeout)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_page_title(self):
        self.driver.get('%s%s' % (self.live_server_url, '/en/studygroup/create/'))
        self.assertTrue(expected_conditions.title_is('Learning circles'))


    def test_courses_tab(self):
        self.driver.get('%s%s' % (self.live_server_url, '/en/studygroup/create/'))
        creation_page = LearningCircleCreationPage(self.driver, self.wait)
        course_cards = self.driver.find_elements(*LearningCircleCreationPageLocators.COURSE_CARDS)
        published_courses = Course.objects.active().filter(unlisted=False).count()

        self.assertTrue(expected_conditions.text_to_be_present_in_element(LearningCircleCreationPageLocators.TAB_1, 'Step 1: Select a Course *'))
        self.assertEqual(len(course_cards), published_courses)


    def test_publish_learning_circle(self):
        user_data = {
            "email": "teddy@test.com",
            "first_name": "Ted",
            "last_name": "Danson",
            "password": "password"
        }
        facilitator = create_user(user_data["email"], user_data["first_name"], user_data["last_name"], user_data["password"])
        confirm_user_email(facilitator)

        self.driver.get('%s%s' % (self.live_server_url, '/en/studygroup/create/'))

        creation_page = LearningCircleCreationPage(self.driver, self.wait)
        creation_page.fill_out_form_correctly()

        creation_page.click_publish_button()
        self.assertTrue(expected_conditions.presence_of_element_located(RegistrationModalLocators.REGISTRATION_MODAL))

        creation_page.click_login_link()
        self.assertTrue(expected_conditions.text_to_be_present_in_element(RegistrationModalLocators.REGISTRATION_MODAL_TITLE, 'Log in'))

        creation_page.fill_out_login_modal(user_data)

        self.assertTrue(expected_conditions.alert_is_present())
        self.assertTrue(expected_conditions.text_to_be_present_in_element(LearningCircleCreationPageLocators.SUCCESS_ALERT, "You're logged in! You can now save or publish your learning circle."))

        overlay = self.driver.find_element(*RegistrationModalLocators.MODAL_OVERLAY)
        self.wait.until(expected_conditions.staleness_of(overlay))

        creation_page.click_publish_button()

        #self.wait.until(expected_conditions.url_changes('%s%s' % (self.live_server_url, '/en/studygroup/create/')))
        self.wait.until(expected_conditions.url_to_be('{}/en/facilitator/'.format(self.live_server_url)))

        published_studygroup = StudyGroup.objects.published().last()
        self.assertEqual(published_studygroup.facilitator, facilitator)


    def test_learning_circle_errors(self):
        user_data = {
            "email": "teddy@test.com",
            "first_name": "Ted",
            "last_name": "Danson",
            "password": "password"
        }
        facilitator = create_user(user_data["email"], user_data["first_name"], user_data["last_name"], user_data["password"])
        self.driver.get('%s%s' % (self.live_server_url, '/en/studygroup/create/'))

        creation_page = LearningCircleCreationPage(self.driver, self.wait)

        creation_page.go_to_tab_5()

        creation_page.click_publish_button()
        self.assertTrue(expected_conditions.presence_of_element_located(RegistrationModalLocators.REGISTRATION_MODAL))

        creation_page.click_login_link()
        self.assertTrue(expected_conditions.text_to_be_present_in_element(RegistrationModalLocators.REGISTRATION_MODAL_TITLE, 'Log in'))

        creation_page.fill_out_login_modal(user_data)

        self.assertTrue(expected_conditions.alert_is_present())
        self.assertTrue(expected_conditions.text_to_be_present_in_element(LearningCircleCreationPageLocators.SUCCESS_ALERT, "You're logged in! You can now save or publish your learning circle."))

        overlay = self.driver.find_element(*RegistrationModalLocators.MODAL_OVERLAY)
        self.wait.until(expected_conditions.staleness_of(overlay))

        creation_page.click_publish_button()

        self.assertTrue(expected_conditions.alert_is_present())
        self.assertTrue(expected_conditions.text_to_be_present_in_element(LearningCircleCreationPageLocators.DANGER_ALERT, "There was a problem saving your learning circle. Please check the error messages in the form and make the necessary changes."))
        creation_page.close_alert()

        self.assertTrue(expected_conditions.text_to_be_present_in_element(LearningCircleCreationPageLocators.TAB_1_TITLE, "Step 1: Select a Course *"))
        self.assertTrue(expected_conditions.presence_of_element_located(LearningCircleCreationPageLocators.ERROR_MESSAGE))

        creation_page.go_to_tab_2()
        self.assertTrue(expected_conditions.presence_of_all_elements_located(LearningCircleCreationPageLocators.ERROR_MESSAGE))

        creation_page.go_to_tab_3()
        self.assertTrue(expected_conditions.presence_of_all_elements_located(LearningCircleCreationPageLocators.ERROR_MESSAGE))

        creation_page.go_to_tab_4()
        self.assertTrue(expected_conditions.presence_of_all_elements_located(LearningCircleCreationPageLocators.ERROR_MESSAGE))

        studygroup_count = StudyGroup.objects.all().count()
        self.assertEqual(studygroup_count, 0)


    def test_save_draft_learning_circle(self):
        user_data = {
            "email": "teddy@test.com",
            "first_name": "Ted",
            "last_name": "Danson",
            "password": "password"
        }
        facilitator = create_user(user_data["email"], user_data["first_name"], user_data["last_name"], user_data["password"])
        self.driver.get('%s%s' % (self.live_server_url, '/en/studygroup/create/'))

        creation_page = LearningCircleCreationPage(self.driver, self.wait)
        creation_page.fill_out_form_correctly()

        creation_page.click_save_button()
        self.assertTrue(expected_conditions.presence_of_element_located(RegistrationModalLocators.REGISTRATION_MODAL))

        creation_page.click_login_link()
        self.assertTrue(expected_conditions.text_to_be_present_in_element(RegistrationModalLocators.REGISTRATION_MODAL_TITLE, 'Log in'))

        creation_page.fill_out_login_modal(user_data)

        self.assertTrue(expected_conditions.alert_is_present())
        self.assertTrue(expected_conditions.text_to_be_present_in_element(LearningCircleCreationPageLocators.SUCCESS_ALERT, "You're logged in! You can now save or publish your learning circle."))

        overlay = self.driver.find_element(*RegistrationModalLocators.MODAL_OVERLAY)
        self.wait.until(expected_conditions.staleness_of(overlay))

        creation_page.click_save_button()

        #self.wait.until(expected_conditions.url_changes('{}/en/studygroup/create/'.format(self.live_server_url)))
        self.wait.until(expected_conditions.url_to_be('{}/en/facilitator/'.format(self.live_server_url)))

        saved_studygroup = StudyGroup.objects.filter(draft=True).last()
        self.assertEqual(saved_studygroup.facilitator, facilitator)


