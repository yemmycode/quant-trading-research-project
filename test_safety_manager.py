
"""
Safety Manager Test

This script tests persistent emergency stop behavior.
It does not connect to a broker.
It does not place orders.
"""

from safety_manager import (
    read_emergency_stop_state,
    activate_emergency_stop,
    deactivate_emergency_stop,
    is_emergency_stop_active,
    require_emergency_stop_inactive
)


def main():
    print("Safety Manager Test")
    print("===================")

    print("\nInitial state:")
    print(read_emergency_stop_state())

    print("\nActivating emergency stop...")
    activate_emergency_stop(
        reason="Testing persistent emergency stop.",
        updated_by="test_safety_manager.py"
    )

    print("State after activation:")
    print(read_emergency_stop_state())
    print("Is active:", is_emergency_stop_active())

    print("\nTesting blocker:")
    try:
        require_emergency_stop_inactive()
    except Exception as e:
        print("Blocked correctly:")
        print(type(e).__name__)
        print(e)

    print("\nDeactivating emergency stop...")
    deactivate_emergency_stop(
        reason="Test completed.",
        updated_by="test_safety_manager.py"
    )

    print("State after deactivation:")
    print(read_emergency_stop_state())
    print("Is active:", is_emergency_stop_active())

    print("\nFinal inactive check:")
    print(require_emergency_stop_inactive())

    print("\nSafety manager test completed.")


if __name__ == "__main__":
    main()
