import allure
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from utilities.pageutils import PageUtils


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.ac = ActionChains(self.driver)
        self.page_utils = PageUtils(self.driver)
        self.ec = ec

    # XPATH Define header Navigation XPath Here
    HEADER_XPATH = "//div[contains(@class, 'header-links')]"
    REGISTER_XPATH = (By.XPATH, HEADER_XPATH + "//a[contains(@href, 'register')]")
    LOGIN_XPATH = (By.XPATH, HEADER_XPATH + "//a[contains(@href, 'login')]")
    LOGOUT_XPATH = (By.XPATH, HEADER_XPATH + "//a[contains(@href, 'logout')]")
    WISHLIST_XPATH = (By.XPATH, HEADER_XPATH + "//a[contains(@href, 'wishlist')]")
    SHOPPING_CART_XPATH = (By.XPATH, HEADER_XPATH + "//a[contains(@href, '/cart')]")

    @allure.step
    def goto_registration_pg(self):
        registration_link = self.driver.find_element(*self.REGISTER_XPATH)
        self.page_utils.scroll_into_view(registration_link)
        registration_link.click()

    @allure.step
    def goto_login_pg(self):
        login_link = self.driver.find_element(*self.LOGIN_XPATH)
        self.page_utils.scroll_into_view(login_link)
        login_link.click()

    @allure.step
    def goto_cart_pg(self):
        cart_link = self.driver.find_element(*self.SHOPPING_CART_XPATH)
        self.page_utils.scroll_into_view(cart_link)
        cart_link.click()
