"""BasePage - shared actions every page object inherits.

Keeps common Selenium operations (click, type, read text) in one
place so individual page objects stay short and readable.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self, url):
        self.driver.get(url)

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type_text(self, locator, text, timeout=15):
        """Type into a field and confirm the value actually registered.

        React controlled inputs can drop keystrokes sent before hydration
        completes (same root cause as swallowed clicks), so re-type until
        the field really holds the expected text.
        """
        react_set_value = """
            const field = arguments[0], value = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value').set;
            setter.call(field, value);
            field.dispatchEvent(new Event('input', { bubbles: true }));
        """
        self.find(locator)
        self.driver.implicitly_wait(0)
        attempt = {"count": 0}
        try:
            def _typed_and_confirmed(driver):
                fields = driver.find_elements(*locator)
                if not fields:
                    return False
                field = fields[0]
                try:
                    if field.get_attribute("value") == text:
                        return True
                    # Native keystrokes first; if React resets the field
                    # (controlled input whose onChange was not wired up in
                    # time), fall back to React's own value setter.
                    if attempt["count"] % 2 == 0:
                        field.clear()
                        field.send_keys(text)
                    else:
                        driver.execute_script(react_set_value, field, text)
                    attempt["count"] += 1
                    return field.get_attribute("value") == text
                except Exception:
                    return False

            WebDriverWait(self.driver, timeout).until(_typed_and_confirmed)
        finally:
            self.driver.implicitly_wait(5)

    def get_text(self, locator):
        return self.find(locator).text

    def is_visible(self, locator):
        try:
            self.find(locator)
            return True
        except Exception:
            return False

    def click_and_expect(self, locator, expected_locator, timeout=15):
        """Click an element and confirm the expected result appears.

        React apps like saucedemo can render buttons before their click
        handlers are attached, silently swallowing early clicks (common on
        slow CI machines). This retries the click until the expected
        element confirms the action actually happened.
        """
        self.driver.implicitly_wait(0)
        attempt = {"count": 0}
        try:
            def _click_until_confirmed(driver):
                if driver.find_elements(*expected_locator):
                    return True
                targets = driver.find_elements(*locator)
                if targets:
                    try:
                        # Alternate native and JavaScript clicks: native
                        # clicks can be silently swallowed by React apps
                        # mid-hydration, while a JS click dispatches the
                        # event directly on the element.
                        if attempt["count"] % 2 == 0:
                            targets[0].click()
                        else:
                            driver.execute_script("arguments[0].click();", targets[0])
                    except Exception:
                        pass
                    attempt["count"] += 1
                return False

            WebDriverWait(self.driver, timeout).until(_click_until_confirmed)
        finally:
            self.driver.implicitly_wait(5)
