
"""
Error Notification System Test

This script tests error recording and resolution.
It does not connect to IBKR.
It does not place orders.
"""

from error_notifier import (
    notify_error,
    notify_message,
    read_error_notifications,
    mark_error_resolved,
    summarize_errors,
    get_error_notifier_status,
)


def main():
    print("Error Notification System Test")
    print("==============================")

    info_result = notify_message(
        component="test_error_notifier",
        message="Testing informational notification.",
        severity="INFO",
        context={"test": True}
    )

    print("\nInfo notification:")
    print(info_result)

    try:
        1 / 0
    except Exception as e:
        error_result = notify_error(
            component="test_error_notifier",
            error=e,
            severity="ERROR",
            context={"operation": "division_test"}
        )

        print("\nError notification:")
        print(error_result)

        resolved = mark_error_resolved(
            error_id=error_result["error_id"],
            resolution_note="Test error resolved."
        )

        print("\nResolved result:")
        print(resolved)

    critical_result = notify_error(
        component="test_error_notifier",
        error="Testing critical message.",
        severity="CRITICAL",
        context={"test": True}
    )

    print("\nCritical notification:")
    print(critical_result)

    print("\nRecent notifications:")
    print(read_error_notifications(limit=10).to_string(index=False))

    print("\nSummary:")
    print(summarize_errors())

    print("\nStatus:")
    print(get_error_notifier_status())

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
