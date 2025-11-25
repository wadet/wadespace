"""
Pytest configuration and hooks for Wade Space Game tests.
"""

import sys


def pytest_runtest_setup(item):
    """Print test name before each test runs."""
    # Get the test name with class if applicable
    test_name = item.nodeid.replace("::", " -> ")
    # Use stderr to bypass pytest capture
    sys.stderr.write(f"\n🧪 Running: {test_name}\n")
    sys.stderr.flush()


def pytest_runtest_logreport(report):
    """Print test result status."""
    if report.when == "call":
        status_symbol = ""
        if report.outcome == "passed":
            status_symbol = "✓ PASSED"
        elif report.outcome == "failed":
            status_symbol = "✗ FAILED"
        elif report.outcome == "skipped":
            status_symbol = "⊘ SKIPPED"
        
        if status_symbol:
            sys.stderr.write(f"   {status_symbol}\n")
            sys.stderr.flush()
