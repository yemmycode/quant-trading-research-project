
"""
Automated Test Runner Test

This script tests the test runner itself.
It does not connect to IBKR.
It does not place orders.
"""

from test_runner import (
    list_available_tests,
    run_single_test_script,
    read_test_results,
    summarize_test_results,
    get_test_runner_status,
)


def main():
    print("Automated Test Runner Test")
    print("==========================")

    print("\nAvailable safe tests:")
    for row in list_available_tests(include_broker_tests=False):
        print(row)

    print("\nRunning one safe test:")
    result = run_single_test_script(
        test_script="test_price_validation.py",
        timeout_seconds=120
    )
    print(result)

    print("\nRecent test results:")
    print(read_test_results(limit=10).to_string(index=False))

    print("\nSummary:")
    print(summarize_test_results())

    print("\nStatus:")
    print(get_test_runner_status())

    print("\nNo broker connection was attempted by this test runner test.")


if __name__ == "__main__":
    main()
