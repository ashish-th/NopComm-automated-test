import os

import allure
import pytest

from PageObjects.NopCommLoginPage import LoginPage


@pytest.mark.usefixtures('setup')
@allure.parent_suite('Account')
@allure.suite('User Login')
@allure.epic("Account")
@pytest.mark.NopCommDemoRegression
class TestMyAccountFunctional:

    @allure.story('NOP-001:Enable Account Login')
    def test_can_login_to_my_account(self, setup, registered_user, guest_user):
        """test to verify Login functionality"""
        self.driver = setup
        self.customer = guest_user  # guest user instance to grab address for that locale
        self.login_pg = LoginPage(self.driver)
        self.login_pg.goto_login_pg()
        self.login_pg.login(registered_user['UserName'], registered_user['Password'])

    @allure.story('NOP-002: Add Save address Feature on Account Portal')
    def test_can_save_address_on_account(self, setup, registered_user, guest_user):
        """test to verify save address feature for a logged-in User on Account Portal"""
        pass
