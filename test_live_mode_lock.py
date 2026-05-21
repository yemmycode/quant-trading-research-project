
"""
Live Mode Lock Test

This script tests whether live mode is safely locked.
It does not enable live trading.
It does not connect to IBKR.
It does not place orders.
"""

from live_mode_lock import (
    evaluate_live_mode_lock,
    require_live_mode_unlocked,
    explain_live_mode_lock
)


def main():
    print("Live Mode Lock Test")
    print("===================")

    lock_eval = evaluate_live_mode_lock()

    print("\nLock Status:")
    print("Status:", lock_eval["status"])
    print("Live Mode Allowed:", lock_eval["live_mode_allowed"])
    print("Message:", lock_eval["message"])

    print("\nPassed Checks:")
    for item in lock_eval["passed_checks"]:
        print("-", item)

    print("\nFailed Checks:")
    for item in lock_eval["failed_checks"]:
        print("-", item)

    print("\nSimplified Explanation:")
    print(explain_live_mode_lock())

    print("\nTesting hard blocker:")
    try:
        require_live_mode_unlocked()
        print("Unexpected: live mode is unlocked.")
    except Exception as e:
        print("Blocked correctly:")
        print(type(e).__name__)
        print(e)

    print("\nTest completed. No live trading was enabled.")


if __name__ == "__main__":
    main()
