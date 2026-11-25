#!/usr/bin/env python3
"""Check the local environment required by the Jaramsae renderer."""
import importlib.util
import sys
from pathlib import Path

def main():
    problems = []
    if sys.version_info < (3, 10):
        problems.append("Python 3.10+ is required.")
    for module, package in (("jsonschema", "jsonschema>=4.22,<5"), ("playwright", "playwright>=1.45,<2")):
        if importlib.util.find_spec(module) is None:
            problems.append(f"Missing dependency: {package}")
    if not problems:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            executable = Path(p.chromium.executable_path)
            if not executable.is_file():
                problems.append("Playwright Chromium is not installed.")
    if problems:
        print("PREFLIGHT_FAILED")
        for item in problems:
            print(f"- {item}")
        print("\nRun:")
        print("  python -m pip install -r requirements.txt")
        print("  python -m playwright install chromium")
        return 1
    print("PREFLIGHT_OK: Python, dependencies and Playwright Chromium are ready.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
