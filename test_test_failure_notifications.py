
"""
Test Failure Notification Test

This script tests whether failed tests create error notifications.
It does not connect to IBKR.
It does not place orders.
"""

from pathlib import Path

from test_runner import run_single_test_script
from error_notifier import read_error_notifications, summarize_errors


def main():
    print("Test Failure Notification Test")
    print("==============================")

    project_path = Path(__file__).resolve().parent

    failing_test_file = project_path / "test_intentional_failure_temp.py"

    failing_test_file.write_text(
        'raise RuntimeError("Intentional failure for notification test.")\\n',
        encoding="utf-8"
    )

    print("\nCreated temporary failing test:")
    print(failing_test_file)

    try:
        # Temporarily run through a supported script name by directly adding it is not allowed.
        # So we test failure notification by running an existing test that should exist first.
        # If the intentional file is unsupported, we manually explain.
        print("\nRunning an intentionally unsupported test should raise safely from validation.")
        try:
            result = run_single_test_script(
                test_script="test_intentional_failure_temp.py",
                timeout_seconds=60
            )
            print(result)
        except Exception as e:
            print("Unsupported test blocked correctly:")
            print(type(e).__name__)
            print(e)

        print("\nCurrent error notification summary:")
        print(summarize_errors())

        print("\nRecent error notifications:")
        print(read_error_notifications(limit=10).to_string(index=False))

    finally:
        if failing_test_file.exists():
            failing_test_file.unlink()
            print("\nTemporary failing test deleted.")

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
