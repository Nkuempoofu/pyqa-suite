# PyQA Suite - Automated Web Testing Framework

A Python + Selenium WebDriver test automation framework built with the Page Object Model design pattern, targeting the [Sauce Demo](https://www.saucedemo.com) e-commerce application.

**Author:** Nkululeko Mpofu | QA Engineer
[LinkedIn](https://www.linkedin.com/in/nkululeko-mpofu) | [Portfolio](https://nkululeko-portfolio.vercel.app)

## Tech Stack

- **Python 3.14** - core language
- **Selenium WebDriver 4** - browser automation
- **pytest** - test runner and assertions
- **Page Object Model (POM)** - maintainable test architecture
- **requests** - REST API testing
- **Allure + pytest-html** - test reporting with screenshots on failure

## Project Structure

```
pyqa-suite/
├── conftest.py          # Shared pytest fixtures (browser setup/teardown)
├── pytest.ini           # Test runner configuration
├── requirements.txt     # Project dependencies
├── pages/               # Page Object Model classes
│   ├── base_page.py     # Shared page actions (click, type, wait)
│   ├── login_page.py    # Login page locators and actions
│   ├── products_page.py # Inventory, sorting, and add-to-cart actions
│   ├── cart_page.py     # Shopping cart actions
│   └── checkout_page.py # Three-step checkout flow
├── tests/               # Test cases
│   ├── test_login.py    # Login scenarios (valid, invalid, locked out)
│   ├── test_products.py # Inventory display, sorting, cart badge
│   ├── test_cart.py     # Cart contents and navigation
│   ├── test_checkout.py # End-to-end purchase, validation, totals
│   └── test_api.py      # REST API tests (GET, POST, PUT, DELETE)
├── utils/
│   └── api_client.py    # Reusable REST API client
└── reports/             # HTML report + Allure results (generated)
```

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run a specific test file
pytest tests/test_login.py
```

## Test Coverage

21 automated test cases across 5 suites:

| Suite | Scenarios |
|-------|-----------|
| Login | Valid credentials, invalid password, locked-out user |
| Products | Inventory display, price sorting, name sorting, cart badge add/remove |
| Cart | Added items appear, continue shopping navigation, empty by default |
| Checkout | Full end-to-end purchase, required field validation, tax calculation |
| API | GET/POST/PUT/DELETE, response schema, 404 handling, response time |

## Reports

Every run generates two reports in `reports/`:

- **report.html** - self-contained HTML report, open directly in any browser
- **allure-results/** - Allure data, rendered as a dashboard in CI (Phase 4)

On any UI test failure, a screenshot of the browser is captured automatically and attached to the Allure report.

More coming: GitHub Actions CI/CD pipeline with live published reports.
