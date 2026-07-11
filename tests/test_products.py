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


@allure.feature("Product Catalogue")
@pytest.mark.ui
class TestKnownDefects:
    """saucedemo intentionally ships defective user accounts. These tests
    document the known defects by asserting they are present - if the
    vendor ever fixes one, the test fails and tells us the app changed."""

    @allure.story("Known defect - problem_user")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    def test_problem_user_has_broken_sorting_defect(self, driver):
        """DEFECT (documented): sorting Z-A does nothing for problem_user.

        Expected for a healthy user: names in reverse alphabetical order.
        Actual for problem_user: order unchanged. This test asserts the
        defect is still present, demonstrating defect isolation per user type.
        """
        from pages.login_page import LoginPage
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(data.PROBLEM_USER, data.PASSWORD)

        products = ProductsPage(driver)
        products.sort_by("za")
        names = products.get_product_names()

        assert names != sorted(names, reverse=True), (
            "problem_user sorting defect appears to be FIXED - "
            "saucedemo has changed; review and update this documented defect"
        )
