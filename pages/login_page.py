"""LoginPage - page object for the saucedemo.com login screen."""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.test_data import BASE_URL


class LoginPage(BasePage):
    URL = BASE_URL

    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")

    def load(self):
        self.open(self.URL)

    def login(self, username, password):
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        # Login either lands on the inventory page or shows an error -
        # confirm one of the two so a swallowed click can't slip through.
        confirmation = (By.CSS_SELECTOR, ".inventory_list, [data-test='error']")
        self.click_and_expect(self.LOGIN_BUTTON, confirmation)

    def get_error_message(self):
        return self.get_text(self.ERROR_MESSAGE)
