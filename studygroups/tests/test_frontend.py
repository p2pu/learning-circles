from django.test import LiveServerTestCase, override_settings, tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from studygroups.models import Course
from custom_registration.models import create_user

import socket

user_data = {
    "email": "teddy@test.com",
    "first_name": "Ted",
    "last_name": "Danson",
    "password": "password"
}

@override_settings(ALLOWED_HOSTS=['*'])  # Disable ALLOW_HOSTS
class BaseTestCase(StaticLiveServerTestCase):
    fixtures = ['test_courses.json', 'test_studygroups.json']
    host = '0.0.0.0'  # Bind to 0.0.0.0 to allow external access

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # user = User.objects.create_user(user_data["email"], user_data["email"], user_data["password"])
        # user = create_user(user_data["email"], user_data["first_name"], user_data["last_name"], user_data["password"])
        # print(user)
        cls.host = socket.gethostbyname(socket.gethostname())
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-web-security')
        cls.driver = webdriver.Remote(
          command_executor='http://selenium:4444/wd/hub',
          desired_capabilities=DesiredCapabilities.CHROME,
          options=chrome_options
        )
        cls.wait = WebDriverWait(cls.driver, 30)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def fill_text_field(self, locator, *text):
        input_field = self.wait.until(expected_conditions.presence_of_element_located(locator))
        input_field.send_keys(*text)


    def fill_out_form_correctly(self):
        course_select_buttons = self.wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".result-item .primary-cta button:first-of-type")))
        course_select_buttons.click()

        next_button = self.wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".action-bar button:last-of-type")))
        next_button.click()
        self.assertTrue(expected_conditions.text_to_be_present_in_element("#react-tabs-2 h4", 'Step 2: Find a Location'))

        city_select = self.wait.until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".city-select .Select-input input")))
        city_select.send_keys("Kitchener")
        self.wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".Select-menu-outer .Select-option")))
        city_select.send_keys(Keys.ARROW_DOWN, Keys.ENTER)

        self.fill_text_field((By.ID, "id_venue_name"), "KPL")
        self.fill_text_field((By.ID, "id_venue_details"), "Hacienda Cafe")
        self.fill_text_field((By.ID, "id_venue_address"), "85 Queen St N, Kitchener")

        next_button = self.wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".action-bar button:last-of-type")))
        next_button.click()
        self.assertTrue(expected_conditions.text_to_be_present_in_element("#react-tabs-3 h4", 'Step 3: Select the Day and Time'))

        self.fill_text_field((By.ID, "id_start_date"), "01/06/2019", Keys.ENTER)
        self.fill_text_field((By.ID, "id_weeks"), Keys.DELETE, "8")

        meeting_time_field = self.driver.find_element(By.NAME, "meeting_time")
        meeting_time_field.click()
        meeting_time_input = self.wait.until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".rc-time-picker-panel-input")))
        meeting_time_input.send_keys("7:00 pm")

        self.fill_text_field((By.ID, "id_duration"), "60")

        next_button = self.wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".action-bar button:last-of-type")))
        next_button.click()
        self.assertTrue(expected_conditions.text_to_be_present_in_element("#react-tabs-4 h4", 'Step 4: Customize'))

        self.fill_text_field((By.ID, "id_description"), "Welcome to my learning circle!")
        self.fill_text_field((By.ID, "id_signup_question"), "What do you want to learn?")
        self.fill_text_field((By.ID, "id_venue_website"), "https://www.kpl.org")

        next_button = self.wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".action-bar button:last-of-type")))
        next_button.click()
        self.assertTrue(expected_conditions.text_to_be_present_in_element("#react-tabs-5 h4", 'Step 5: Finalize'))

        self.fill_text_field((By.ID, "id_facilitator_goal"), "Have a great learning circle")
        self.fill_text_field((By.ID, "id_facilitator_concerns"), "Nothing really")


    def test_page_title(self):
        self.driver.get('%s%s' % (self.live_server_url, '/en/studygroup/create/'))
        self.assertTrue(expected_conditions.title_is('Learning circles'))


    def test_courses_tab(self):
        self.driver.get('%s%s' % (self.live_server_url, '/en/studygroup/create/'))
        course_cards = self.driver.find_elements(By.CSS_SELECTOR, "#react-tabs-1 .search-results .result-item")
        published_courses = Course.objects.active().filter(unlisted=False).count()
        self.assertTrue(expected_conditions.text_to_be_present_in_element("#react-tabs-1 h4", 'Step 1: Select a Course *'))
        self.assertEqual(len(course_cards), published_courses)


    def test_publish_learning_circle(self):
        facilitator = create_user(user_data["email"], user_data["first_name"], user_data["last_name"], user_data["password"])

        self.driver.get('%s%s' % (self.live_server_url, '/en/studygroup/create/'))
        self.fill_out_form_correctly()

        self.driver.find_element(By.CSS_SELECTOR, ".action-bar button.publish").click()

        self.assertTrue(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".registration-modal")))

        self.driver.find_element_by_link_text('log in.').click()
        self.assertTrue(expected_conditions.text_to_be_present_in_element(".registration-modal-content h4", 'Log in'))

        self.fill_text_field((By.ID, "id_email"), user_data["email"])
        self.fill_text_field((By.ID, "id_password"), user_data["password"])
        self.driver.find_element(By.CSS_SELECTOR, ".modal-actions button[type=submit]").click()

        self.assertTrue(expected_conditions.alert_is_present())
        self.assertTrue(expected_conditions.text_to_be_present_in_element(".alert.alert-success", "You're logged in! You can now save or publish your learning circle."))

        overlay = self.driver.find_element(By.CSS_SELECTOR, ".modal-overlay")
        self.wait.until(expected_conditions.staleness_of(overlay))

        publish_button = self.wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".action-bar button.publish")))
        publish_button.click()

        self.wait.until(expected_conditions.url_changes('%s%s' % (self.live_server_url, '/en/studygroup/create/')))
        self.assertTrue(expected_conditions.url_contains('/en/facilitator/study_group/published'))







