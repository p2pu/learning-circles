from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from e2e.tests.selenium.locators import LearningCircleCreationPageLocators
from e2e.tests.selenium.locators import RegistrationModalLocators

import datetime

class BasePage(object):

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def fill_text_field(self, locator, *text):
        input_field = self.driver.find_element(*locator)
        try:
            input_field.clear()
        except:
            pass
        finally:
            input_field.send_keys(*text)


class LearningCircleCreationPage(BasePage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Date needs to be 4 days in the future - UI disables earlier dates
        self.start_date = (datetime.datetime.now() + datetime.timedelta(days=5)).date().strftime("%Y%m%d")

    def fill_out_form_correctly(self):
        self.select_first_course()

        self.click_next_button()

        self.fill_city_select_field("Kitchener")
        self.fill_text_field(LearningCircleCreationPageLocators.VENUE_NAME_FIELD, "KPL")
        self.fill_text_field(LearningCircleCreationPageLocators.VENUE_DETAILS_FIELD, "Hacienda Cafe")
        self.fill_text_field(LearningCircleCreationPageLocators.VENUE_ADDRESS_FIELD, "85 Queen St N, Kitchener")

        self.click_next_button()

        self.fill_text_field(LearningCircleCreationPageLocators.START_DATE_FIELD, self.start_date)
        self.fill_text_field(LearningCircleCreationPageLocators.WEEKS_FIELD, "8")

        self.fill_text_field(LearningCircleCreationPageLocators.MEETING_TIME_FIELD, "7:00 PM", Keys.ENTER)
        self.fill_text_field(LearningCircleCreationPageLocators.DURATION_FIELD, "60")

        self.click_next_button()

        self.fill_text_field(LearningCircleCreationPageLocators.TITLE_FIELD, "Sharon's Learning Circle")
        self.fill_text_field(LearningCircleCreationPageLocators.DESCRIPTION_FIELD, "Welcome to my learning circle!")
        self.fill_text_field(LearningCircleCreationPageLocators.COURSE_DESCRIPTION_FIELD, "This is the course description")
        self.fill_text_field(LearningCircleCreationPageLocators.SIGNUP_QUESTION_FIELD, "What do you want to learn?")
        self.fill_text_field(LearningCircleCreationPageLocators.VENUE_WEBSITE_FIELD, "https://www.kpl.org")

        self.click_next_button()

        self.fill_text_field(LearningCircleCreationPageLocators.FACILITATOR_GOAL_FIELD, "Have a great learning circle")
        self.fill_text_field(LearningCircleCreationPageLocators.FACILITATOR_CONCERNS_FIELD, "Nothing really")


    def select_first_course(self):
        course_cards = self.wait.until(expected_conditions.visibility_of_all_elements_located(LearningCircleCreationPageLocators.COURSE_CARDS))
        self.wait.until(expected_conditions.text_to_be_present_in_element(LearningCircleCreationPageLocators.FIRST_COURSE_TITLE, "Academic Writing"))

        course_select_button = self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.FIRST_COURSE_BUTTON))
        self.driver.execute_script("return arguments[0].click();", course_select_button)
        # course_select_button.click()
        # wait until search container is gone
        self.wait.until_not(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, '.search-container')))
        remove_link = self.wait.until(expected_conditions.visibility_of_element_located(LearningCircleCreationPageLocators. REMOVE_COURSE_SELECTION_LINK))
        assert 'Remove selection' in remove_link.text


    def fill_city_select_field(self, location):
        city_select = self.wait.until(expected_conditions.visibility_of_element_located(LearningCircleCreationPageLocators.CITY_SELECT_INPUT))
        city_select.send_keys(location)
        self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.CITY_SELECT_OPTION))
        city_select.send_keys(Keys.ENTER)

    def click_next_button(self):
        next_button = self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.NEXT_TAB_BUTTON))
        next_button.click()

    def click_publish_button(self):
        publish_button = self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.PUBLISH_BUTTON))
        publish_button.click()

    def click_save_button(self):
        publish_button = self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.SAVE_BUTTON))
        publish_button.click()

    def click_login_link(self):
        self.driver.find_element_by_css_selector('.registration-modal-content button:first-child').click()

    def fill_out_login_modal(self, user_data):
        self.fill_text_field(RegistrationModalLocators.EMAIL_FIELD, user_data["email"])
        self.fill_text_field(RegistrationModalLocators.PASSWORD_FIELD, user_data["password"])
        self.driver.find_element(*RegistrationModalLocators.SUBMIT_BUTTON).click()

    def go_to_tab_1(self):
        tab_button = self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.TAB_1))
        tab_button.click()

    def go_to_tab_2(self):
        tab_button = self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.TAB_2))
        tab_button.click()

    def go_to_tab_3(self):
        tab_button = self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.TAB_3))
        tab_button.click()

    def go_to_tab_4(self):
        tab_button = self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.TAB_4))
        tab_button.click()

    def go_to_tab_5(self):
        tab_button = self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.TAB_5))
        tab_button.click()

    def close_alert(self):
        close_button = self.wait.until(expected_conditions.element_to_be_clickable(LearningCircleCreationPageLocators.ALERT_CLOSE_BUTTON))
        close_button.click()
