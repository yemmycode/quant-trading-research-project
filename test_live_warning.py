
"""
Live Trading Warning Test

This script tests live warning acknowledgement.
It does not enable live trading.
It does not connect to IBKR.
It does not place orders.
"""

from live_warning import (
    read_warning_state,
    acknowledge_live_warning,
    reset_live_warning_acknowledgement,
    is_live_warning_acknowledged,
    require_live_warning_acknowledged
)


def main():
    print("Live Trading Warning Test")
    print("=========================")

    print("\nResetting warning acknowledgement...")
    reset_live_warning_acknowledgement()

    print("Acknowledged:", is_live_warning_acknowledged())

    print("\nTesting blocker:")
    try:
        require_live_warning_acknowledged()
        print("Unexpected: warning already acknowledged.")
    except Exception as e:
        print("Blocked correctly:")
        print(type(e).__name__)
        print(e)

    print("\nAcknowledging warning...")
    acknowledge_live_warning(
        acknowledged_by="test_live_warning.py",
        notes="Testing warning acknowledgement."
    )

    print("Acknowledged:", is_live_warning_acknowledged())
    print("State:")
    print(read_warning_state())

    print("\nFinal check:")
    print(require_live_warning_acknowledged())

    print("\nTest completed. No live trading was enabled.")


if __name__ == "__main__":
    main()
