"""Tag Allure results with the browser they ran on.

When the CI matrix runs the suite on Chrome and Firefox, both result
sets merge into one report. Without tagging, Allure would treat the
same test on two browsers as retries of one test. This script renames
each test with a [browser] suffix and makes its historyId unique so
both appear side by side.

Usage: python scripts/tag_browser.py <allure_results_dir> <browser>
"""
import json
import sys
from pathlib import Path


def main():
    results_dir = Path(sys.argv[1])
    browser = sys.argv[2].lower()

    count = 0
    for path in results_dir.glob("*-result.json"):
        with open(path, encoding="utf-8") as f:
            result = json.load(f)

        result["name"] = f"{result.get('name', '?')} [{browser}]"
        if result.get("historyId"):
            result["historyId"] = f"{result['historyId']}-{browser}"
        result.setdefault("parameters", []).append(
            {"name": "browser", "value": browser}
        )
        result.setdefault("labels", []).append(
            {"name": "tag", "value": browser}
        )

        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f)
        count += 1

    print(f"Tagged {count} results as [{browser}]")


if __name__ == "__main__":
    main()
