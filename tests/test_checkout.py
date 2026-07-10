"""Checkout test cases - the full end-to-end purchase flow."""
from pages.products_page import ProductsPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


class TestCheckout:

    def test_complete_checkout_end_to_end(self, logged_in_driver):
        """A user can add a product, check out, and see the order confirmation."""
        products = ProductsPage(logged_in_driver)
        products.add_product_to_cart("Sauce Labs Backpack")
        products.open_cart()

        cart = CartPage(logged_in_driver)
        cart.checkout()

        checkout = CheckoutPage(logged_in_driver)
        checkout.fill_customer_info("Nkululeko", "Mpofu", "0001")
        checkout.finish_order()

        assert "Thank you for your order" in checkout.get_confirmation_message()

    def test_checkout_requires_first_name(self, logged_in_driver):
        """Submitting customer info without a first name shows an error."""
        products = ProductsPage(logged_in_driver)
        products.add_product_to_cart("Sauce Labs Backpack")
        products.open_cart()

        cart = CartPage(logged_in_driver)
        cart.checkout()

        checkout = CheckoutPage(logged_in_driver)
        checkout.fill_customer_info("", "Mpofu", "0001")

        assert "First Name is required" in checkout.get_error_message()

    def test_order_total_includes_tax(self, logged_in_driver):
        """The order summary shows a total greater than the item price alone."""
        products = ProductsPage(logged_in_driver)
        products.add_product_to_cart("Sauce Labs Backpack")
        products.open_cart()

        cart = CartPage(logged_in_driver)
        cart.checkout()

        checkout = CheckoutPage(logged_in_driver)
        checkout.fill_customer_info("Nkululeko", "Mpofu", "0001")

        total_text = checkout.get_total_text()
        total = float(total_text.replace("Total: $", ""))
        assert total > 29.99, f"Total {total} should be item price 29.99 plus tax"
