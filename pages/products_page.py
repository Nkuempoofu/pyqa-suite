"""ProductsPage - page object for the saucedemo.com inventory screen."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from pages.base_page import BasePage


class ProductsPage(BasePage):
    TITLE = (By.CLASS_NAME, "title")
    INVENTORY_ITEMS = (By.CLASS_NAME, "inventory_item")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    ITEM_PRICES = (By.CLASS_NAME, "inventory_item_price")
    SORT_DROPDOWN = (By.CLASS_NAME, "product_sort_container")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")

    def get_title(self):
        return self.get_text(self.TITLE)

    def get_product_count(self):
        return len(self.driver.find_elements(*self.INVENTORY_ITEMS))

    def get_product_names(self):
        return [el.text for el in self.driver.find_elements(*self.ITEM_NAMES)]

    def get_product_prices(self):
        elements = self.driver.find_elements(*self.ITEM_PRICES)
        return [float(el.text.replace("$", "")) for el in elements]

    def sort_by(self, value):
        """value options: az, za, lohi, hilo"""
        Select(self.find(self.SORT_DROPDOWN)).select_by_value(value)

    def add_product_to_cart(self, product_name):
        """Click 'Add to cart' for a product by its display name."""
        slug = product_name.lower().replace(" ", "-")
        button = (By.ID, f"add-to-cart-{slug}")
        self.click(button)

    def remove_product_from_cart(self, product_name):
        slug = product_name.lower().replace(" ", "-")
        button = (By.ID, f"remove-{slug}")
        self.click(button)

    def get_cart_count(self):
        if self.is_visible(self.CART_BADGE):
            return int(self.get_text(self.CART_BADGE))
        return 0

    def open_cart(self):
        self.click(self.CART_LINK)
