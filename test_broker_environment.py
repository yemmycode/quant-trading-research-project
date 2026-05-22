
"""
Broker Environment Classifier Test

This script classifies the current broker environment.
It does not connect to IBKR.
It does not place orders.
"""

from broker_environment import (
    get_broker_environment_snapshot,
    classify_broker_environment,
    get_environment_recommendation
)


def main():
    print("Broker Environment Classifier Test")
    print("==================================")

    print("\nSnapshot:")
    print(get_broker_environment_snapshot())

    print("\nClassification:")
    classification = classify_broker_environment()
    print(classification)

    print("\nRecommendation:")
    print(get_environment_recommendation())

    print("\nNo broker connection was attempted.")
    print("No orders were placed.")


if __name__ == "__main__":
    main()
