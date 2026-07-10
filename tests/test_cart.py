"""Shopping cart test cases - adding, viewing, and removing items."""
import allure
import pytest

from pages.products_page import ProductsPage
from pages.cart_page import CartPage
from utils import test_data as data


@allure.feature("Shopping Cart")
@pytest.mark.ui
class TestCart:

    @allure.story("Cart contents")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_added_products_appear_in_cart(self, logged_in_driver):
        """Products added on the inventory page show up in the cart."""
        products = ProductsPage(logged_in_driver)
        products.add_product_to_cart(data.BACKPACK)
        products.add_product_to_cart(data.BIKE_LIGHT)
        products.open_cart()

        cart = CartPage(logged_in_driver)
        assert cart.get_item_count() == 2
        names = cart.get_item_names()
        assert data.BACKPACK in names
        assert data.BIKE_LIGHT in names

    @allure.story("Navigation")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_continue_shopping_returns_to_products(self, logged_in_driver):
        """Continue shopping navigates back to the inventory page."""
        products = ProductsPage(logged_in_driver)
        products.open_cart()

        cart = CartPage(logged_in_driver)
        cart.continue_shopping()

        assert "inventory" in logged_in_driver.current_url

    @allure.story("Cart contents")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_cart_is_empty_by_default(self, logged_in_driver):
        """A fresh session has no items in the cart."""
        products = ProductsPage(logged_in_driver)
        products.open_cart()

        cart = CartPage(logged_in_driver)
        assert cart.get_item_count() == 0
