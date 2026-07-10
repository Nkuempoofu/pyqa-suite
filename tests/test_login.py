"""Login test cases for saucedemo.com.

Covers the classic three scenarios every QA engineer starts with:
valid login, invalid password, and locked-out user.
"""
from pages.login_page import LoginPage


class TestLogin:

    def test_valid_login(self, driver):
        """A standard user with correct credentials lands on the inventory page."""
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login("standard_user", "secret_sauce")

        assert "inventory" in driver.current_url, "User was not redirected to the inventory page"

    def test_invalid_password_shows_error(self, driver):
        """A wrong password shows the correct error message and blocks entry."""
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login("standard_user", "wrong_password")

        error = login_page.get_error_message()
        assert "Username and password do not match" in error

    def test_locked_out_user_is_blocked(self, driver):
        """A locked-out user cannot log in even with correct credentials."""
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login("locked_out_user", "secret_sauce")

        error = login_page.get_error_message()
        assert "locked out" in error
