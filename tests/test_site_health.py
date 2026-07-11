"""Generic site health checks - run against ANY website.

Unlike the saucedemo suite (which knows that app's pages and buttons),
these tests make no assumptions about the site under test. Point them
at any URL via the TARGET_URL environment variable:

    TARGET_URL=https://example.com pytest -m health        (bash)
    $env:TARGET_URL="https://example.com"; pytest -m health (PowerShell)

Or run them from GitHub: Actions -> Site Health Check -> Run workflow.
"""
import os
from urllib.parse import urljoin, urlparse

import allure
import pytest
import requests

TARGET_URL = os.environ.get("TARGET_URL", "").strip()

pytestmark = [
    pytest.mark.health,
    pytest.mark.skipif(not TARGET_URL, reason="TARGET_URL not set - health checks run on demand"),
]

HEADERS = {"User-Agent": "Mozilla/5.0 (PyQA Suite health check; +https://github.com/Nkuempoofu/pyqa-suite)"}
TIMEOUT = 15


@pytest.fixture(scope="module")
def homepage():
    return requests.get(TARGET_URL, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)


@allure.feature("Site Health")
class TestSiteHealth:

    @allure.story("Availability")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_homepage_is_reachable(self, homepage):
        """The site responds without a client or server error."""
        assert homepage.status_code < 400, (
            f"{TARGET_URL} returned HTTP {homepage.status_code}"
        )

    @allure.story("Availability")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_uses_https(self, homepage):
        """The final URL (after redirects) is served over HTTPS."""
        assert homepage.url.startswith("https://"), (
            f"Site is not served over HTTPS: {homepage.url}"
        )

    @allure.story("Performance")
    @allure.severity(allure.severity_level.NORMAL)
    def test_responds_within_five_seconds(self, homepage):
        """The homepage responds in a reasonable time."""
        elapsed = homepage.elapsed.total_seconds()
        assert elapsed < 5, f"Homepage took {elapsed:.1f}s to respond"

    @allure.story("Rendering")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_page_renders_with_title(self, driver):
        """The page loads in a real browser and has a non-empty title."""
        driver.get(TARGET_URL)
        assert driver.title.strip(), "Page rendered with an empty <title>"

    @allure.story("Rendering")
    @allure.severity(allure.severity_level.NORMAL)
    def test_page_has_mobile_viewport(self, driver):
        """A responsive viewport meta tag is present (mobile readiness)."""
        driver.get(TARGET_URL)
        tags = driver.execute_script(
            "return document.querySelectorAll(\"meta[name='viewport']\").length"
        )
        assert tags > 0, "No <meta name='viewport'> tag - page may not be mobile-friendly"

    @allure.story("Links")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_no_broken_links_on_homepage(self, driver):
        """Internal links on the homepage do not lead to 404s (first 15 sampled)."""
        driver.get(TARGET_URL)
        hrefs = driver.execute_script(
            "return Array.from(document.querySelectorAll('a[href]'), a => a.href)"
        )
        site_host = urlparse(TARGET_URL).netloc
        internal = []
        for href in hrefs:
            parsed = urlparse(urljoin(TARGET_URL, href))
            if parsed.scheme in ("http", "https") and parsed.netloc == site_host:
                clean = parsed._replace(fragment="").geturl()
                if clean not in internal:
                    internal.append(clean)

        broken = []
        for link in internal[:15]:
            try:
                resp = requests.get(link, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
                if resp.status_code in (404, 410) or resp.status_code >= 500:
                    broken.append(f"{link} -> HTTP {resp.status_code}")
            except requests.RequestException as exc:
                broken.append(f"{link} -> {type(exc).__name__}")

        assert not broken, "Broken links found:\n" + "\n".join(broken)

    @allure.story("Console")
    @allure.severity(allure.severity_level.MINOR)
    def test_no_severe_console_errors(self, driver):
        """The browser console logs no SEVERE JavaScript errors on load."""
        driver.get(TARGET_URL)
        try:
            logs = driver.get_log("browser")
        except Exception:
            pytest.skip("Browser console logs not available in this driver")
        severe = [
            entry["message"] for entry in logs
            if entry.get("level") == "SEVERE" and "favicon" not in entry.get("message", "")
        ]
        assert not severe, "SEVERE console errors:\n" + "\n".join(severe[:5])


@pytest.fixture(scope="module")
def axe_source():
    """Download the axe-core accessibility engine once per session."""
    resp = requests.get(
        "https://cdn.jsdelivr.net/npm/axe-core@4.10.2/axe.min.js",
        headers=HEADERS, timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return resp.text


def run_axe(driver, axe_source):
    """Inject axe-core into the current page and return its violation list."""
    driver.execute_script(axe_source)
    return driver.execute_async_script(
        """
        const done = arguments[arguments.length - 1];
        axe.run(document, { resultTypes: ['violations'] })
           .then(r => done(r.violations))
           .catch(e => done([{ id: 'axe-error', impact: 'critical',
                               description: String(e), nodes: [] }]));
        """
    )


@allure.feature("Site Health")
class TestAccessibility:
    """WCAG accessibility checks powered by the axe-core engine -
    the same engine behind Lighthouse and browser a11y devtools."""

    @allure.story("Accessibility")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_no_critical_accessibility_violations(self, driver, axe_source):
        """The page has no CRITICAL WCAG violations (axe-core audit)."""
        import json as _json
        driver.get(TARGET_URL)
        violations = run_axe(driver, axe_source)

        allure.attach(
            _json.dumps(violations, indent=2),
            name="axe-full-results",
            attachment_type=allure.attachment_type.JSON,
        )

        critical = [v for v in violations if v.get("impact") == "critical"]
        summary = [
            f"{v['id']} ({len(v.get('nodes', []))} elements): {v.get('description', '')}"
            for v in critical
        ]
        assert not critical, (
            f"{len(critical)} critical WCAG violations:\n" + "\n".join(summary)
        )

    @allure.story("Accessibility")
    @allure.severity(allure.severity_level.NORMAL)
    def test_accessibility_violation_summary(self, driver, axe_source):
        """Report all WCAG violations by impact; fail only if serious ones exceed 5."""
        driver.get(TARGET_URL)
        violations = run_axe(driver, axe_source)

        by_impact = {}
        for v in violations:
            by_impact.setdefault(v.get("impact", "unknown"), []).append(v["id"])

        report = "\n".join(f"{impact}: {len(ids)} - {', '.join(ids)}" for impact, ids in by_impact.items())
        allure.attach(report or "No violations found",
                      name="a11y-summary", attachment_type=allure.attachment_type.TEXT)

        serious = by_impact.get("serious", [])
        assert len(serious) <= 5, (
            f"{len(serious)} serious WCAG violations (threshold 5):\n{report}"
        )
