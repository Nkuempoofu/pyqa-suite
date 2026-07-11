"""Central test data for the PyQA Suite framework.

Keeping URLs, credentials, and product names in one place means
a change to the application under test is a one-line fix here,
not a hunt through every test file.
"""

BASE_URL = "https://www.saucedemo.com"
API_BASE_URL = "https://jsonplaceholder.typicode.com"

# saucedemo.com publishes these demo credentials on its login page
STANDARD_USER = "standard_user"
LOCKED_OUT_USER = "locked_out_user"
PROBLEM_USER = "problem_user"              # ships with intentional UI defects
PERFORMANCE_GLITCH_USER = "performance_glitch_user"  # intentionally slow
PASSWORD = "secret_sauce"
WRONG_PASSWORD = "wrong_password"

# Products used in cart and checkout tests
BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"
BACKPACK_PRICE = 29.99

# Checkout customer details
FIRST_NAME = "Nkululeko"
LAST_NAME = "Mpofu"
POSTAL_CODE = "0001"

# Expected messages
ERROR_BAD_CREDENTIALS = "Username and password do not match"
ERROR_LOCKED_OUT = "locked out"
ERROR_USERNAME_REQUIRED = "Username is required"
ERROR_FIRST_NAME_REQUIRED = "First Name is required"
ORDER_CONFIRMATION = "Thank you for your order"
