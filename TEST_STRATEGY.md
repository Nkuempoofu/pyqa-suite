# Test Strategy - PyQA Suite

**Author:** Nkululeko Mpofu, QA Engineer
**System under test:** [Sauce Demo](https://www.saucedemo.com) (e-commerce web app) + [JSONPlaceholder](https://jsonplaceholder.typicode.com) (REST API)
**Live results:** [nkuempoofu.github.io/pyqa-suite](https://nkuempoofu.github.io/pyqa-suite/)

---

## 1. Purpose

This document defines the testing approach, scope, priorities, and quality gates for PyQA Suite. It exists so that anyone - a developer, a hiring manager, or a future teammate - can understand *why* the suite tests what it tests, not just *what* it runs.

## 2. Test objectives

1. Verify that the critical revenue path (login -> browse -> cart -> checkout) works on every change.
2. Catch regressions in existing functionality before they reach a release.
3. Validate the API contract (status codes, response schemas, error handling) independently of the UI.
4. Provide fast, trustworthy feedback: full suite in under 3 minutes, smoke checks in under 30 seconds.

## 3. Scope

**In scope**

| Layer | Coverage |
|-------|----------|
| UI (Selenium) | Authentication, product catalogue, sorting, cart, three-step checkout |
| API (requests) | CRUD operations, response schemas, 404 handling, response times |
| Generic health | Availability, HTTPS, broken links, mobile viewport, console errors - runnable against any URL |

**Out of scope (deliberate)**

- Load and stress testing (different toolchain - would use Locust/k6)
- Penetration testing (requires authorisation and a dedicated security scope)
- Email, payment-gateway, and third-party integrations (not present in the demo app)

## 4. Test approach

### 4.1 Test levels and types

- **Smoke** (`pytest -m smoke`) - 4 blocker-level tests covering the critical path. Run first; if these fail, deeper testing is pointless.
- **Regression** (`pytest -m regression`) - full functional depth: negative paths, sorting, validation messages, totals.
- **API** (`pytest -m api`) - contract tests that run without a browser (~6 seconds), so backend regressions surface even faster.
- **Health** (`pytest -m health`) - environment-agnostic checks parameterised by `TARGET_URL`, triggered on demand from the Actions tab.

### 4.2 Risk-based prioritisation

Test depth follows business risk, marked in-code with Allure severity:

| Feature | Risk if broken | Severity | Depth |
|---------|---------------|----------|-------|
| Checkout / payment path | Direct revenue loss | Blocker | End-to-end + validation + totals |
| Authentication | No user can enter | Blocker/Critical | Positive + negative + locked-out |
| Cart operations | Abandoned purchases | Critical | Add/remove/badge/contents |
| API contract | Downstream consumers break | Critical | Full CRUD + schemas |
| Sorting / catalogue display | Degraded experience | Normal | Representative cases |
| Response times | Gradual user attrition | Minor | Threshold checks |

### 4.3 Automation design principles

- **Page Object Model** - locators and page behaviour live in `pages/`; tests read as business scenarios.
- **Verified interactions** - every navigation click and form input confirms its outcome and retries with a JavaScript fallback, because the app under test (a React SPA) can silently drop events during hydration. Flaky tests destroy trust in a suite; this design keeps trust.
- **Central test data** - URLs, credentials, and expected messages live in `utils/test_data.py`; an application change is a one-line fix.
- **Independent tests** - every test gets a fresh browser and logs in via fixture; no test depends on another's leftover state.

## 5. Test environment

| Context | Details |
|---------|---------|
| Local | Windows 11, Python 3.14, visible or headless Chrome |
| CI | Ubuntu (GitHub Actions), Python 3.12, headless Chrome, on every push + nightly at 02:00 SAST |
| Browser management | webdriver-manager resolves the matching chromedriver automatically |

## 6. Entry and exit criteria

**Entry (before a run is meaningful)**
- Dependencies install cleanly from `requirements.txt`
- Target site/API reachable
- Smoke subset passes

**Exit (definition of a green release)**
- 100% of blocker and critical tests pass
- No unreviewed failures - every red test is triaged (defect vs. flake vs. expected change) before merging
- Reports published and archived (Allure + HTML artifact)

## 7. Defect management

1. A failing test automatically captures a **screenshot** attached to the Allure report.
2. The failure is triaged: application defect, test defect, or environment issue.
3. Application defects are logged with reproduction steps, severity, expected vs. actual, and evidence (in a team context: JIRA; here: GitHub Issues).
4. Fixes are verified by re-running the failing test plus the surrounding regression pack, never the failing test alone.

## 8. Metrics and reporting

- **Pass rate per run** and **trend across runs** - published live to the [dashboard](https://nkuempoofu.github.io/pyqa-suite/)
- **Slowest tests** - reviewed for optimisation on the [analytics page](https://nkuempoofu.github.io/pyqa-suite/graphs.html)
- **Severity coverage** - confirms depth follows risk (section 4.2)
- Full drill-down (steps, timings, screenshots) in the [Allure report](https://nkuempoofu.github.io/pyqa-suite/report/)

## 9. Maintenance

- Test packs are reviewed when the application under test changes; locator drift is contained to page objects.
- The nightly scheduled run detects environmental rot (site changes, dependency issues) even when no code changes.
- Suite additions follow the marker taxonomy so smoke stays fast as regression grows.
