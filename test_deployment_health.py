
"""
Deployment Health Check Test

This script checks whether the app is running locally or in cloud-like environment.
It does not connect to IBKR beyond optional localhost socket checks.
It does not place orders.
"""

from deployment_health import run_deployment_health_check


def main():
    print("Deployment Health Check Test")
    print("============================")

    result = run_deployment_health_check()

    print("\nStatus:", result["status"])
    print("Recommendation:", result["recommendation"])

    print("\nRuntime:")
    print(result["runtime"])

    print("\nIBKR Localhost Checks:")
    for row in result["localhost_ibkr"]:
        print(row)

    print("\nFeature Matrix:")
    for row in result["feature_matrix"]:
        print(row)

    print("\nNo broker orders were placed.")


if __name__ == "__main__":
    main()
