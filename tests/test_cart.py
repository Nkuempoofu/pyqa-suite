"""Shopping cart test cases - adding, viewing, and removing items."""
from pages.products_page import ProductsPage
from pages.cart_page import CartPage


class TestCart:

    def test_added_products_appear_in_cart(self, logged_in_driver):
        """Products added on the inventory page show up in the cart."""
        products = ProductsPage(logged_in_driver)
        products.add_product_to_cart("Sauce Labs Backpack")
        products.add_product_to_cart("Sauce Labs Bike Light")
        products.open_cart()

        cart = CartPage(logged_in_driver)
        assert cart.get_item_count() == 2
        names = cart.get_item_names()
        assert "Sauce Labs Backpack" in names
        assert "Sauce Labs Bike Light" in names

    def test_continue_shopping_returns_to_products(self, logged_in_driver):
        """Continue shopping navigates back to the inventory page."""
        products = ProductsPage(logged_in_driver)
        products.open_cart()

        cart = CartPage(logged_in_driver)
        cart.continue_shopping()

        assert "inventory" in logged_in_driver.current_url

    def test_cart_is_empty_by_default(self, logged_in_driver):
        """A fresh session has no items in the cart."""
        products = ProductsPage(logged_in_driver)
        products.open_cart()

        cart = CartPage(logged_in_driver)
        assert cart.get_item_count() == 0
