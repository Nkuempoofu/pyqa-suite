"""Checkout test cases - the full end-to-end purchase flow."""
import allure
import pytest

from pages.products_page import ProductsPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from utils import test_data as data


@allure.feature("Checkout")
@pytest.mark.ui
class TestCheckout:

    def _add_backpack_and_go_to_checkout(self, driver):
        """Shared journey: add a backpack, open the cart, start checkout."""
        products = ProductsPage(driver)
        products.add_product_to_cart(data.BACKPACK)
        products.open_cart()
        CartPage(driver).checkout()
        return CheckoutPage(driver)

    @allure.story("End-to-end purchase")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_complete_checkout_end_to_end(self, logged_in_driver):
        """A user can add a product, check out, and see the order confirmation."""
        checkout = self._add_backpack_and_go_to_checkout(logged_in_driver)
        checkout.fill_customer_info(data.FIRST_NAME, data.LAST_NAME, data.POSTAL_CODE)
        checkout.finish_order()

        assert data.ORDER_CONFIRMATION in checkout.get_confirmation_message()

    @allure.story("Form validation")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_checkout_requires_first_name(self, logged_in_driver):
        """Submitting customer info without a first name shows an error."""
        checkout = self._add_backpack_and_go_to_checkout(logged_in_driver)
        checkout.fill_customer_info("", data.LAST_NAME, data.POSTAL_CODE)

        assert data.ERROR_FIRST_NAME_REQUIRED in checkout.get_error_message()

    @allure.story("Order totals")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    def test_order_total_includes_tax(self, logged_in_driver):
        """The order summary shows a total greater than the item price alone."""
        checkout = self._add_backpack_and_go_to_checkout(logged_in_driver)
        checkout.fill_customer_info(data.FIRST_NAME, data.LAST_NAME, data.POSTAL_CODE)

        total = float(checkout.get_total_text().replace("Total: $", ""))
        assert total > data.BACKPACK_PRICE, (
            f"Total {total} should be item price {data.BACKPACK_PRICE} plus tax"
        )
