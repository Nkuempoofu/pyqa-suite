"""CheckoutPage - page object for the saucedemo.com checkout flow.

Covers all three checkout steps: customer information,
order overview, and the confirmation screen.
"""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    FINISH_BUTTON = (By.ID, "finish")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-test='error']")
    SUMMARY_TOTAL = (By.CLASS_NAME, "summary_total_label")
    CONFIRMATION_HEADER = (By.CLASS_NAME, "complete-header")

    def fill_customer_info(self, first_name, last_name, postal_code):
        self.type_text(self.FIRST_NAME, first_name)
        self.type_text(self.LAST_NAME, last_name)
        self.type_text(self.POSTAL_CODE, postal_code)
        self.click(self.CONTINUE_BUTTON)

    def get_error_message(self):
        return self.get_text(self.ERROR_MESSAGE)

    def get_total_text(self):
        return self.get_text(self.SUMMARY_TOTAL)

    def finish_order(self):
        self.click(self.FINISH_BUTTON)

    def get_confirmation_message(self):
        return self.get_text(self.CONFIRMATION_HEADER)
