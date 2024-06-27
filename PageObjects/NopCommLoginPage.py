from selenium.webdriver.common.by import By

from PageObjects.BasePage import BasePage


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    # Define your XPATHS here

    EMAIL = (By.ID, "Email")
    PASSWORD = (By.ID, "Password")
    LOGIN_BTN = (By.XPATH, "//button[contains(@class, 'login-button')]")

    def login(self, username, password):
        self.wait.until(self.ec.visibility_of_element_located(self.EMAIL)).send_keys(username)
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.LOGIN_BTN).click()
        self.wait.until(self.ec.invisibility_of_element_located(self.LOGIN_XPATH))
