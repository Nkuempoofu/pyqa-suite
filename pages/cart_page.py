"""CartPage - page object for the saucedemo.com shopping cart."""
from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class CartPage(BasePage):
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    CONTINUE_SHOPPING = (By.ID, "continue-shopping")

    def get_item_count(self):
        return len(self.driver.find_elements(*self.CART_ITEMS))

    def get_item_names(self):
        return [el.text for el in self.driver.find_elements(*self.ITEM_NAMES)]

    def checkout(self):
        """Start checkout and confirm the customer info form loaded."""
        first_name_field = (By.ID, "first-name")
        self.click_and_expect(self.CHECKOUT_BUTTON, first_name_field)

    def continue_shopping(self):
        """Return to the inventory and confirm the product list loaded."""
        inventory_list = (By.CLASS_NAME, "inventory_list")
        self.click_and_expect(self.CONTINUE_SHOPPING, inventory_list)
