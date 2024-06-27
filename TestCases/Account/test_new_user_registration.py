import os

import allure
import pytest
from selenium.webdriver.support.wait import WebDriverWait

from PageObjects.NopCommRegistrationPage import RegistrationPage
from utilities.customer import CustomGEN, CountryLocale


@allure.parent_suite('Account')
@allure.suite('User Registration')
@pytest.mark.usefixtures('setup')
@pytest.mark.NopCommDemoRegression
class TestAccountRegistration:
    def local_setup(self):
        self.customer = CustomGEN(CountryLocale.US)
        self.Register = RegistrationPage(self.driver)
        self.wait = WebDriverWait(self.driver, 30)

    # ***************************************************************************************************************

    def test_can_register_user(self, setup):
        """Validate -  can register for an account from UI"""
        self.driver = setup
        self.local_setup()
        self.Register.goto_registration_pg()
        self.Register.submit_registration(self.customer)

    # ***************************************************************************************************************
