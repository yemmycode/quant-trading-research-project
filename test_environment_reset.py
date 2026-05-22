
"""
Environment Reset Checklist Test

This script tests the environment reset checklist.
It does not change .env.
It does not connect to IBKR.
It does not place orders.
"""

from environment_reset import (
    read_reset_state,
    bulk_update_reset_checklist,
    evaluate_environment_reset,
    reset_checklist_to_dataframe,
    reset_checklist_to_default
)


def main():
    print("Environment Reset Checklist Test")
    print("===============================")

    print("\nResetting checklist to default...")
    reset_checklist_to_default()

    print("\nInitial evaluation:")
    print(evaluate_environment_reset())

    print("\nUpdating sample reset items...")
    bulk_update_reset_checklist(
        {
            "ibkr_read_only_true_in_env": True,
            "ibkr_enable_orders_false_in_env": True,
            "allow_live_trading_false": True,
            "live_trading_enabled_false": True,
            "broker_environment_panel_checked": True,
        },
        updated_by="test_environment_reset.py",
        notes="Testing environment reset checklist."
    )

    print("\nUpdated evaluation:")
    print(evaluate_environment_reset())

    print("\nChecklist dataframe:")
    print(reset_checklist_to_dataframe().to_string(index=False))

    print("\nState:")
    print(read_reset_state())

    print("\nTest completed. No environment settings were changed.")


if __name__ == "__main__":
    main()
