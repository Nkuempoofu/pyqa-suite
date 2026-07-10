# PyQA Suite - Automated Web Testing Framework

[![Test Suite](https://github.com/Nkuempoofu/pyqa-suite/actions/workflows/tests.yml/badge.svg)](https://github.com/Nkuempoofu/pyqa-suite/actions/workflows/tests.yml)

A Python + Selenium WebDriver test automation framework built with the Page Object Model design pattern, targeting the [Sauce Demo](https://www.saucedemo.com) e-commerce application.

**Author:** Nkululeko Mpofu | QA Engineer
[LinkedIn](https://www.linkedin.com/in/nkululeko-mpofu) | [Portfolio](https://nkululeko-portfolio.vercel.app)

**Live Allure report:** [nkuempoofu.github.io/pyqa-suite](https://nkuempoofu.github.io/pyqa-suite/)

## Tech Stack

- **Python 3.14** - core language
- **Selenium WebDriver 4** - browser automation
- **pytest** - test runner, fixtures, and markers
- **Page Object Model (POM)** - maintainable test architecture
- **requests** - REST API testing
- **Allure + pytest-html** - test reporting with screenshots on failure
- **GitHub Actions** - CI pipeline running the suite on every push

## Project Structure

```
pyqa-suite/
├── .github/workflows/
│   └── tests.yml        # CI pipeline: headless run + Allure to GitHub Pages
├── conftest.py          # Fixtures: browser setup, login state, failure screenshots
├── pytest.ini           # Runner config, report paths, marker registry
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
│   ├── api_client.py    # Reusable REST API client
│   └── test_data.py     # Central URLs, credentials, and expected messages
└── reports/             # HTML report + Allure results (generated)
```

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full suite
pytest

# Run only the fast critical-path checks
pytest -m smoke

# Run only API tests (no browser needed, ~6 seconds)
pytest -m api

# Run only browser tests
pytest -m ui

# Run headless (no visible browser window)
HEADLESS=1 pytest          # macOS/Linux
$env:HEADLESS="1"; pytest  # Windows PowerShell
```

## Test Coverage

21 automated test cases across 5 suites:

| Suite | Scenarios | Markers |
|-------|-----------|---------|
| Login | Valid credentials, invalid password, locked-out user | ui, smoke, regression |
| Products | Inventory display, price sorting, name sorting, cart badge add/remove | ui, smoke, regression |
| Cart | Added items appear, continue shopping navigation, empty by default | ui, regression |
| Checkout | Full end-to-end purchase, required field validation, tax calculation | ui, smoke, regression |
| API | GET/POST/PUT/DELETE, response schema, 404 handling, response time | api, smoke, regression |

## Reports

Every run generates two reports in `reports/`:

- **report.html** - self-contained HTML report, open directly in any browser
- **allure-results/** - Allure data, rendered as a live dashboard by the CI pipeline

On any UI test failure, a screenshot of the browser is captured automatically and attached to the Allure report.

## CI/CD

The GitHub Actions pipeline runs on every push and pull request:

1. Installs Python and dependencies on a clean Ubuntu runner
2. Executes all 21 tests with headless Chrome
3. Uploads the HTML report as a build artifact
4. Builds the Allure dashboard (with run history) and publishes it to GitHub Pages
