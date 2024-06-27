import json
import os
import random
import secrets
import string
import time

import allure
from pytest_check import check
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By


class PageUtils:

    def __init__(self, driver):
        self.driver = driver
        self.ac = ActionChains(self.driver)

    def click(self, element):
        self.driver.execute_script('arguments[0].click();', element)

    def scroll_into_view(self, element):
        self.driver.execute_script('arguments[0].scrollIntoView(true);', element)

    def scroll_into_center(self, element):
        script = """
            var element = arguments[0];
            var rect = element.getBoundingClientRect();
            var x = (window.innerWidth - rect.width) / 2;
            var y = (window.innerHeight - rect.height) / 2;
            window.scrollTo(x, y);
        """
        self.driver.execute_script(script, element)

    def enter_text(self, element, text):
        """js executor method , alternative to selenium send keys"""
        self.driver.execute_script(f"arguments[0].value='{text}';", element)

    def highlight_element(self, element, color="#abdbe3"):
        random_color = '#{:06x}'.format(random.randint(0, 0xFFFFFF))
        border_color = '#{:06x}'.format(random.randint(0, 0xFFFFFF))
        self.driver.execute_script(
            f"arguments[0].setAttribute('style', 'background-color: {random_color}; border: 1px dotted {border_color}; border-style: "
            "inset');",
            element)

    def is_element_visible_in_viewport(self, element) -> bool:
        """
        pass in a webelement , checks if element is in the viewport ,
        :param element:
        :return: true if entire element is visible on current viewport else false
        """
        return self.driver.execute_script("var elem = arguments[0],                 "
                                          "  box = elem.getBoundingClientRect(),    "
                                          "  cx = box.left + box.width / 2,         "
                                          "  cy = box.top + box.height / 2,         "
                                          "  e = document.elementFromPoint(cx, cy); "
                                          "for (; e; e = e.parentElement) {         "
                                          "  if (e === elem)                        "
                                          "    return true;                         "
                                          "}                                        "
                                          "return false;                            "
                                          , element)

    def is_elements_visible_in_viewport(self, elements: []):
        for element in elements:
            self.highlight_element(element)
            self.is_element_visible_in_viewport(element)

    def is_element_partially_visible_in_viewport(self, element) -> bool:
        """
        pass in a webelement , checks if element is partially present in the viewport ,
        :param element:
        :return: true if top, left and right  element is visible on current viewport else false
        """
        elem_left_bound = element.location.get('x')
        elem_top_bound = element.location.get('y')
        elem_width = element.size.get('width')
        elem_height = element.size.get('height')
        elem_right_bound = elem_left_bound + elem_width
        elem_lower_bound = elem_top_bound + elem_height

        win_upper_bound = self.driver.execute_script('return window.pageYOffset')
        win_left_bound = self.driver.execute_script('return window.pageXOffset')
        win_width = self.driver.execute_script('return document.documentElement.clientWidth')
        win_height = self.driver.execute_script('return document.documentElement.clientHeight')
        win_right_bound = win_left_bound + win_width
        win_lower_bound = win_upper_bound + win_height

        return all((win_left_bound <= elem_left_bound,
                    win_right_bound >= elem_right_bound,
                    win_upper_bound <= elem_top_bound,)
                   # win_lower_bound >= elem_lower_bound)
                   )

    def scroll_to_the_bottom(self):
        pause_time = 2
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:  # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(pause_time)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def allure_step_with_screenshot(self, step_desc, full_page=False):
        with allure.step(title=step_desc):
            name = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
            file_name = name + ".png"
            if full_page:
                self.make_header_static()
                self.scroll_to_the_bottom()
                original_size = self.driver.get_window_size()
                required_width = self.driver.execute_script('return document.body.parentNode.scrollWidth')
                required_height = self.driver.execute_script('return document.body.parentNode.scrollHeight')
                self.driver.set_window_size(required_width, required_height)
                self.driver.find_element(By.TAG_NAME, 'body').screenshot(file_name)  # avoids scrollbar
                self.driver.set_window_size(original_size['width'], original_size['height'])
                allure.attach.file(file_name, attachment_type=allure.attachment_type.PNG)
                os.remove(file_name)
                self.make_header_static(make_static=False)
            else:
                self.driver.save_screenshot(file_name)
                allure.attach.file(file_name, attachment_type=allure.attachment_type.PNG)
                os.remove(file_name)

    def step_generator_with_element_screenshot(self, locator, step_desc='', ):
        @allure.step(title=step_desc)
        def steps():
            element = self.driver.find_element(*locator)
            name = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
            file_name = name + ".png"
            element.screenshot(file_name)
            allure.attach.file(file_name, attachment_type=allure.attachment_type.PNG)
            os.remove(file_name)

        steps()

    def make_header_static(self, make_static=True):
        """
        FullPage screenshot implemented for chrome requires header to be not sticky
        this method can be used to toggle position of header element
        :param make_static: True - makes header static(not sticky), False - resets position back to sticky
        :return: None
        """
        self.driver.implicitly_wait(2)
        if make_static:
            try:
                element = self.driver.find_element(By.XPATH, "//header[contains(@class, 'page-header')]")
                self.driver.execute_script('arguments[0].style.position="static";', element)
            except NoSuchElementException:
                pass
        else:
            try:
                element = self.driver.find_element(By.XPATH, "//header[contains(@class, 'page-header')]")
                self.driver.execute_script('arguments[0].style.position="relative";', element)
            except NoSuchElementException:
                pass
        self.driver.implicitly_wait(30)

    def step_generator(self, step_desc):
        @allure.step(title=step_desc)
        def step():
            """Place Holder method to generate test steps without any attachment"""
            pass

        step()

    def allure_step_with_json(self, step_desc, data):
        """creates a step on allure reporter with a json file for the data """
        with allure.step(title=step_desc):
            name = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
            json_obj = json.dumps(data, indent=4)
            file_name = name + ".json"
            with open(file_name, 'w') as outfile:
                outfile.write(json_obj)
            allure.attach.file(file_name, attachment_type=allure.attachment_type.JSON)
            os.remove(file_name)

    @allure.step('Page Validation: "{page_name}"')
    @check.check_func
    def validate_pg(self, page_name, locators):
        """Pass in a page and expected list of locators
        checks for presence of all locators passed within the list"""
        self.allure_step_with_screenshot(step_desc=page_name)
        for locator in locators:
            print(f'searching for {locator}')
            loc_size = len(self.driver.find_elements(*locator))
            assert loc_size >= 1, f'{page_name}:{locator} not found'

    def step_generator_with_text(self, text, details='step details'):
        self.logger.info(text)
        allure.attach(f'{text}', details,
                      allure.attachment_type.TEXT)

    @allure.step('Setting Driver Geo Location to  {1}, {2}')
    def set_driver_geo_loc(self, latitude, longitude):
        """
        sets current driver geolocation to specified lat and long
        :param latitude:
        :param longitude:
        :return:
        """
        script = 'window.navigator.geolocation.getCurrentPosition = function(success) {\n' \
                 '\tvar position = {\n' \
                 '\t\t"coords": {\n' \
                 f'\t\t\t"latitude":{latitude} ,\n' \
                 f'\t\t\t"longitude":{longitude}\n' \
                 '\t\t}\n' \
                 '\t};\n' \
                 '\tsuccess(position);\n' \
                 '}'
        self.driver.execute_script(script)

    def get_pref_loc(self):
        """returns driver pref loc cookie"""
        all_cookies = self.driver.get_cookies()
        for item in all_cookies:
            if item["name"] == "pref_loc":
                value = item["value"]
                return value

    def update_cookie(self, cookie_name, **kwargs):
        """
        # Update the cookie with new attributes
        # cookie['value'] = 'new_value'
        # cookie['domain'] = 'example.com'
        # cookie['path'] = '/'
        # cookie['expiry'] = 1234567890  # New expiry time in seconds since epoch
        :param cookie_name:
        :param kwargs:
        :return: None
        """
        # Get the current cookies
        cookies = self.driver.get_cookies()

        # Find the cookie you want to update
        with allure.step(f"Cookie '{cookie_name}' updated with: {kwargs}"):
            for cookie in cookies:
                if cookie['name'] == cookie_name:
                    # Update the cookie with new attributes
                    for key, value in kwargs.items():
                        cookie[key] = value

                    # Delete the old cookie
                    self.driver.delete_cookie(cookie_name)

                    # Add the updated cookie
                    self.driver.add_cookie(cookie)

                    print(f"Cookie '{cookie_name}' updated with: {kwargs}")
                    self.allure_step_with_json(step_desc=cookie_name, data=cookie)
                    return

        print(f"Cookie '{cookie_name}' not found")
