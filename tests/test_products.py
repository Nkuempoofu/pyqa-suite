"""Product page test cases - inventory display, sorting, and cart badge."""
import allure
import pytest

from pages.products_page import ProductsPage
from utils import test_data as data


@allure.feature("Product Catalogue")
@pytest.mark.ui
class TestProducts:

    @allure.story("Inventory display")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_all_products_are_displayed(self, logged_in_driver):
        """The inventory page shows all 6 products."""
        products = ProductsPage(logged_in_driver)

        assert products.get_title() == "Products"
        assert products.get_product_count() == 6

    @allure.story("Sorting")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_sort_products_by_price_low_to_high(self, logged_in_driver):
        """Sorting low-to-high puts prices in ascending order."""
        products = ProductsPage(logged_in_driver)
        products.sort_by("lohi")

        prices = products.get_product_prices()
        assert prices == sorted(prices), f"Prices not in ascending order: {prices}"

    @allure.story("Sorting")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_sort_products_by_name_z_to_a(self, logged_in_driver):
        """Sorting Z-to-A puts product names in reverse alphabetical order."""
        products = ProductsPage(logged_in_driver)
        products.sort_by("za")

        names = products.get_product_names()
        assert names == sorted(names, reverse=True), f"Names not in Z-A order: {names}"

    @allure.story("Cart badge")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_add_product_updates_cart_badge(self, logged_in_driver):
        """Adding a product shows 1 on the cart badge."""
        products = ProductsPage(logged_in_driver)
        products.add_product_to_cart(data.BACKPACK)

        assert products.get_cart_count() == 1

    @allure.story("Cart badge")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_remove_product_clears_cart_badge(self, logged_in_driver):
        """Removing the only product clears the cart badge."""
        products = ProductsPage(logged_in_driver)
        products.add_product_to_cart(data.BACKPACK)
        products.remove_product_from_cart(data.BACKPACK)

        assert products.get_cart_count() == 0
