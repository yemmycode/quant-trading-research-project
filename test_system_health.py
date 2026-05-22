
"""
System Health Check Test

This script runs local system health diagnostics.
It does not connect to IBKR.
It does not place orders.
"""

from system_health import run_system_health_check


def main():
    print("System Health Check Test")
    print("========================")

    result = run_system_health_check()

    print("\nStatus:", result["status"])
    print("Overall OK:", result["overall_ok"])
    print("Recommendation:", result["recommendation"])

    print("\nSummary:")
    print(result["summary"])

    print("\nModule Import Results:")
    for row in result["modules"]:
        print(row)

    print("\nConfig Safety:")
    print(result["config_safety"])

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
