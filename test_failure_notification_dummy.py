
"""
Dummy Failure Notification Test

This script intentionally fails so the test runner can prove that
failed tests create error notifications.

It does not connect to IBKR.
It does not place orders.
"""

raise RuntimeError("Intentional dummy failure to test error notification integration.")
