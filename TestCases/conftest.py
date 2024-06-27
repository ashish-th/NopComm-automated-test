import json
import os
import random

import pytest
import requests
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from yaml import SafeLoader

import root as r
from utilities.Reporting.slackTemplate import SlackTemplate, TestResult
from utilities.customer import CustomGEN, CountryLocale


@pytest.fixture()
def setup(request):
    url = "https://demo.nopcommerce.com/"
    os.environ["Base_URL"] = url
    global driver, env
    browser = request.config.getoption("browser")
    headless = request.config.getoption("headless")
    env = request.config.getoption("env")
    remote = request.config.getoption("remote")
    hub_url = os.environ.get('SELENIUM_HUB_URL')
    print(hub_url)
    options = set_chrome_options()
    if remote.upper() == 'Y' and hub_url:
        options.add_argument("--headless")
        driver = webdriver.Remote(command_executor=hub_url, options=options)
    else:
        if headless.upper() == 'Y':
            options.add_argument("--headless")
        if browser == 'chrome':
            s = Service()
            driver = webdriver.Chrome(service=s, options=options)
    if not os.path.exists(os.path.join(r.ROOT_DIR, 'AllureDir/environment.properties')):
        update__env_properties(driver)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(30)
    driver.set_script_timeout(90)

    driver.get(url)
    # return driver
    request.cls.driver = driver
    yield driver
    get_browser_log_entries(driver)
    driver.quit()


import logging


def get_browser_log_entries(driver, log_level=logging.ERROR):
    """Fetch browser logs using Selenium WebDriver and log them using Python logging."""
    loglevels = {'NOTSET': 0, 'DEBUG': 10, 'INFO': 20, 'WARNING': 30, 'ERROR': 40, 'SEVERE': 40, 'CRITICAL': 50}

    # Initialize a logger
    browserlog = logging.getLogger("chrome")
    browserlog.setLevel(log_level)

    # Get browser logs
    slurped_logs = driver.get_log('browser')
    for entry in slurped_logs:
        # Convert browser log to Python log format
        rec = browserlog.makeRecord("%s.%s" % (browserlog.name, entry['source']),
                                    loglevels.get(entry['level'], logging.NOTSET), '.', 40,
                                    entry['message'], None, None)
        rec.created = entry['timestamp'] / 1000  # Log using original timestamp (us -> ms)
        try:
            # Add browser log to Python log
            browserlog.handle(rec)
        except Exception as e:
            print(f"Error handling log entry: {e}")

    # Return fetched logs
    return slurped_logs


def set_loc_cookie(url, loc):
    """
    This function adds site specific cookie to browser session
    :param url:
    :param loc:
    :return:
    """
    driver.get(url)
    all_cookies = driver.get_cookies()
    for item in all_cookies:
        if item["name"] == "pref_loc":
            driver.delete_cookie("pref_loc")
    to_add = {"name": "pref_loc", "value": loc}
    driver.add_cookie(to_add)
    driver.get(url)
    logging.info(url)


def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome", help="my option: type1 or type2")
    parser.addoption("--env", action="store", default="demo", help="my option: type1 or type2")
    parser.addoption("--headless", action="store", default="n", help="my option: y,n")
    parser.addoption("--repeat", action="store", help="Number of times to repeat each test")
    parser.addoption("--remote", action="store", default='y', help="flag to run test in Selenium Grid")
    parser.addoption('--slack_report_link', action='store', dest='slack_report_link',
                     default='https://www.google.com/',
                     help='Set the report link'
                     )


def pytest_configure(config):
    os.environ["browser"] = config.getoption('browser')
    os.environ["env"] = config.getoption('env')
    os.environ["Marker"] = config.getoption("-m")


def set_chrome_options():
    options = webdriver.ChromeOptions()
    options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
    )
    prefs = {"profile.default_content_setting_values.notifications": 2,
             "profile.default_content_settings.geolocation": 2}
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("prefs", prefs)
    custom_header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/74.0.3729.169 Safari/537.36'}
    options.add_argument('--disable-gpu')
    options.add_argument(f"user-agent={custom_header}")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-infobars')
    options.add_argument("--disable-extensions")
    options.accept_insecure_certs = True
    options.add_argument("--safebrowsing-disable-auto-update ")
    options.add_argument("--disable-background-networking")
    options.add_argument("--no-proxy-server")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--disable-gpu")
    options.add_argument("--force-device-scale-factor=1")
    return options


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)
    if report.when == 'call':
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            pass
            # step_generator("Failure screenshot")


def update__env_properties(driver_instance):
    root = r.ROOT_DIR
    file = os.path.join(root, 'AllureDir/environment.properties')
    msg = f'''
    Marker: {os.environ["Marker"]}
    URL: {os.environ["Base_URL"]}
    Browser: {driver_instance.capabilities["browserName"].upper()}
    Version: {driver_instance.capabilities["browserVersion"]}
    Platform: {driver_instance.capabilities["platformName"].upper()}
    '''
    with open(file, 'a+') as fp:
        fp.write(msg + '\n')


# send Report to Slack
@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    yield
    debug_mode = 'JENKINS_URL' not in os.environ
    print(debug_mode)
    WEBHOOK_URL = "https://hooks.slack.com/services/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"

    # special check for pytest-xdist plugin,  we do not want to send report for each worker.
    if hasattr(terminalreporter.config, 'workerinput'):
        return
    test_result = TestResult()
    test_result.failed = len(terminalreporter.stats.get('failed', []))
    test_result.passed = len(terminalreporter.stats.get('passed', []))
    test_result.skipped = len(terminalreporter.stats.get('skipped', []))
    test_result.error = len(terminalreporter.stats.get('error', []))
    test_result.xfailed = len(terminalreporter.stats.get("xfailed", []))
    test_result.xpassed = len(terminalreporter.stats.get("xpassed", []))
    test_result.deselected = len(terminalreporter.stats.get("deselected", []))
    test_result.failed_list = [report.nodeid.split('::')[-1]
                               for report in terminalreporter.stats.get('failed', [])]
    prop = get_properties(os.environ["Marker"])
    report_link = config.option.slack_report_link
    if prop is not None and not debug_mode:
        template = SlackTemplate(result=test_result, properties=prop, link=report_link, env=prop)
        response = requests.post(
            WEBHOOK_URL, data=json.dumps(
                template.constructed_message_format()),
            headers={'Content-Type': 'application/json'}
        )
        print(response.raise_for_status())


def get_properties(name):
    """Get Env Properties from prop.yaml"""
    root = r.ROOT_DIR
    try:
        file = os.path.join(root, 'prop.yaml')
        with open(file) as f:
            data = yaml.load(f, Loader=SafeLoader)
            return data[name] if name in data.keys() else data['Test']
    except Exception as e:
        print(e)
        pass


@pytest.fixture
def registered_user():
    """# fixture that provides a registered user based on env marker passed to test
    :returns {'UserName': 'example@example.net', 'Password': 'Password'}"""
    env = os.environ["env"]
    root = r.ROOT_DIR
    file = os.path.join(root, 'Data/users.json')
    with open(file, 'r+') as json_file:
        data = json.load(json_file)
        try:
            data_list = data[env]
            return data_list[random.randint(0, len(data_list) - 1)]
        except KeyError:
            print(f"Credential for provided environment {env} not found")


@pytest.fixture
def guest_user():
    """
    :return: fixture returns a guest customer object based on env marker passed to test
    example: 1)--env='uat-us' returns a US customer with US address
            2) --env='uat-ca' returns a Canadian Customer and so on
    """
    entered_locale = os.environ["env"]
    if entered_locale.upper().__contains__('US'):
        return CustomGEN(CountryLocale.US)
    elif entered_locale.upper().__contains__('CA'):
        return CustomGEN(CountryLocale.CA)
    elif entered_locale.upper().__contains__('UK'):
        return CustomGEN(CountryLocale.UK)
