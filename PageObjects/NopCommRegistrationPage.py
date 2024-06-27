import random

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from PageObjects.BasePage import BasePage
from utilities.customer import CustomGEN


class RegistrationPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    # Define your XPATHS here

    GENDER = (By.ID, "gender-male")
    FIRST_NAME = (By.ID, "FirstName")
    LAST_NAME = (By.ID, "LastName")
    DOB_DAY = (By.NAME, "DateOfBirthDay")
    DOB_MONTH = (By.NAME, "DateOfBirthMonth")
    DOB_YEAR = (By.NAME, "DateOfBirthYear")
    EMAIL = (By.ID, "Email")
    COMPANY = (By.ID, "Company")
    PASSWORD = (By.ID, "Password")
    CONFIRM_PASSWORD = (By.ID, "ConfirmPassword")
    REGISTER = (By.ID, "register-button")
    REGISTRATION_COMPLETED = (By.XPATH, "//div[contains(text(), 'registration completed')]")

    # Define Page methods

    def submit_registration(self, customer: CustomGEN):
        with allure.step('Select gender'):
            self.driver.find_element(*self.GENDER).click()

        with allure.step('Enter FirstName'):
            self.driver.find_element(*self.FIRST_NAME).send_keys(customer.firstname)

        with allure.step('Enter LastName'):
            self.driver.find_element(*self.LAST_NAME).send_keys(customer.lastname)
        self.select_date_of_birth()

        with allure.step('Enter Email'):
            self.driver.find_element(*self.EMAIL).send_keys(customer.email)

        with allure.step('Enter Password'):
            self.driver.find_element(*self.PASSWORD).send_keys(customer.password)

        with allure.step('Confirm Password'):
            self.driver.find_element(*self.CONFIRM_PASSWORD).send_keys(customer.password)

        with allure.step("Submit Registration"):
            self.page_utils.allure_step_with_screenshot('Form', full_page=True)
        #     self.driver.find_element(*self.REGISTER).click()
        #
        # with allure.step('Verify Registration Confirmation is displayed'):
        #     self.wait.until(self.ec.visibility_of_element_located(self.REGISTRATION_COMPLETED))

    @allure.step
    def select_date_of_birth(self):
        day = Select(self.driver.find_element(*self.DOB_DAY))
        month = Select(self.driver.find_element(*self.DOB_MONTH))
        year = Select(self.driver.find_element(*self.DOB_YEAR))

        day.select_by_value(str(random.randint(1, 30)))
        month.select_by_value(str(random.randint(1, 12)))
        year.select_by_value(str(random.randint(1914, 2024)))
