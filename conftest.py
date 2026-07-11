"""Shared pytest fixtures for the PyQA Suite framework.

The `driver` fixture gives every test a fresh Chrome browser
and closes it automatically when the test finishes. On failure,
a screenshot is attached to the Allure report automatically.
"""
import os
import platform
import sys

import allure
import pytest
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="session", autouse=True)
def allure_environment(request):
    """Write environment details into the Allure results for the report."""
    results_dir = request.config.getoption("--alluredir", default=None)
    if results_dir:
        os.makedirs(results_dir, exist_ok=True)
        lines = [
            f"Python={platform.python_version()}",
            f"Selenium={selenium.__version__}",
            f"OS={platform.system()} {platform.release()}",
            "Browser=Chrome (headless in CI)",
            "Target.Site=https://www.saucedemo.com",
            "API.Under.Test=https://jsonplaceholder.typicode.com",
        ]
        path = os.path.join(results_dir, "environment.properties")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


@pytest.fixture(scope="session")
def driver_path():
    """Download/locate chromedriver once for the whole test session."""
    return ChromeDriverManager().install()


@pytest.fixture
def driver(driver_path):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    # CI servers have no display, so run headless there.
    # Set HEADLESS=1 locally to do the same on your own machine.
    if os.environ.get("CI") or os.environ.get("HEADLESS"):
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    driver.implicitly_wait(5)

    yield driver

    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to the Allure report when a browser test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if driver is not None:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="failure-screenshot",
                attachment_type=allure.attachment_type.PNG,
            )


@pytest.fixture
def logged_in_driver(driver):
    """A browser already logged in as the standard user, sitting on the products page."""
    from pages.login_page import LoginPage
    from utils import test_data as data

    login_page = LoginPage(driver)
    login_page.load()
    login_page.login(data.STANDARD_USER, data.PASSWORD)
    return driver
