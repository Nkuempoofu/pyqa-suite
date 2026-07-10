"""Login test cases for saucedemo.com.

Covers the classic three scenarios every QA engineer starts with:
valid login, invalid password, and locked-out user.
"""
import allure
import pytest

from pages.login_page import LoginPage
from utils import test_data as data


@allure.feature("Authentication")
@pytest.mark.ui
class TestLogin:

    @allure.story("Valid login")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_valid_login(self, driver):
        """A standard user with correct credentials lands on the inventory page."""
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(data.STANDARD_USER, data.PASSWORD)

        assert "inventory" in driver.current_url, "User was not redirected to the inventory page"

    @allure.story("Invalid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_invalid_password_shows_error(self, driver):
        """A wrong password shows the correct error message and blocks entry."""
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(data.STANDARD_USER, data.WRONG_PASSWORD)

        assert data.ERROR_BAD_CREDENTIALS in login_page.get_error_message()

    @allure.story("Locked-out user")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_locked_out_user_is_blocked(self, driver):
        """A locked-out user cannot log in even with correct credentials."""
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(data.LOCKED_OUT_USER, data.PASSWORD)

        assert data.ERROR_LOCKED_OUT in login_page.get_error_message()
