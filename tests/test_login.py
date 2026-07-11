"""Login test cases for saucedemo.com.

Data-driven: the same scenarios run across multiple user types and
credential combinations via @pytest.mark.parametrize, so adding a new
case is one line of data, not a new test function.
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
    @pytest.mark.parametrize("username", [
        data.STANDARD_USER,
        data.PROBLEM_USER,
        data.PERFORMANCE_GLITCH_USER,
    ])
    def test_valid_users_can_login(self, driver, username):
        """Every valid user type lands on the inventory page - including the
        intentionally slow performance_glitch_user, which exercises the
        framework's explicit waits."""
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, data.PASSWORD)

        assert "inventory" in driver.current_url, (
            f"{username} was not redirected to the inventory page"
        )

    @allure.story("Invalid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.parametrize("username,password,expected_error", [
        (data.STANDARD_USER, data.WRONG_PASSWORD, data.ERROR_BAD_CREDENTIALS),
        ("unknown_user", data.PASSWORD, data.ERROR_BAD_CREDENTIALS),
        ("", data.PASSWORD, data.ERROR_USERNAME_REQUIRED),
    ])
    def test_invalid_credentials_are_rejected(self, driver, username, password, expected_error):
        """Wrong password, unknown user, and missing username each show
        the correct error message and block entry."""
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, password)

        assert expected_error in login_page.get_error_message()
        assert "inventory" not in driver.current_url

    @allure.story("Locked-out user")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_locked_out_user_is_blocked(self, driver):
        """A locked-out user cannot log in even with correct credentials."""
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(data.LOCKED_OUT_USER, data.PASSWORD)

        assert data.ERROR_LOCKED_OUT in login_page.get_error_message()
