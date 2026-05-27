
"""
Dashboard Structure Map

This module defines how the Streamlit dashboard should be organized
during the consolidation phase.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from datetime import datetime


DASHBOARD_GROUPS = {
    "1. Trading Control Center": {
        "purpose": "Main daily paper-trading decision workflow.",
        "priority": "primary",
        "sections": [
            "Trading Control Center",
            "Trading Control Center History",
        ],
    },
    "2. Portfolio & Orders": {
        "purpose": "Portfolio state, order lifecycle, fills, slippage, and broker snapshots.",
        "priority": "core_support",
        "sections": [
            "Portfolio Overview",
            "Broker Account Snapshot",
            "Unified Order State Manager",
            "Fill and Slippage Tracking",
            "SQLite Trading Database",
        ],
    },
    "3. Safety & Readiness": {
        "purpose": "Safety gates before broker testing or any future live readiness.",
        "priority": "safety",
        "sections": [
            "Emergency Stop",
            "Broker Environment Safety Panel",
            "Environment Reset Checklist",
            "Live Readiness Checklist",
            "Live Mode Lock",
            "Live Warning",
            "Live Order Dry Run",
            "Market Hours Awareness",
            "Real Price Validation",
            "Position-Aware Signal Execution",
            "Duplicate Order Guard",
        ],
    },
    "4. System Admin": {
        "purpose": "Diagnostics, deployment, testing, and error review.",
        "priority": "admin",
        "sections": [
            "System Health Check Dashboard",
            "Deployment Health Check",
            "Error Notification System",
            "Automated Test Runner",
        ],
    },
    "5. Documentation & Architecture": {
        "purpose": "Architecture, deployment limitations, readiness policy, and project documentation.",
        "priority": "documentation",
        "sections": [
            "Secure Broker Architecture Plan",
            "System Consolidation Plan",
            "IBKR Setup Checklist",
        ],
    },
}


def get_dashboard_structure():
    """
    Return the target dashboard structure.
    """

    rows = []

    for group_name, group_data in DASHBOARD_GROUPS.items():
        for section in group_data["sections"]:
            rows.append({
                "group": group_name,
                "priority": group_data["priority"],
                "purpose": group_data["purpose"],
                "section": section,
            })

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "groups": DASHBOARD_GROUPS,
        "rows": rows,
        "recommendation": (
            "Use Trading Control Center as the primary daily workflow. "
            "Treat other sections as support/admin panels."
        ),
    }


def get_dashboard_cleanup_rules():
    """
    Return dashboard cleanup rules for consolidation.
    """

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rules": [
            "Do not add new dashboard sections unless they support the core workflow.",
            "Trading Control Center must remain the main working screen.",
            "Support tools should remain below the main workflow.",
            "Avoid editing large app.py blocks without syntax checks.",
            "Any new dashboard insertion must be followed by py_compile syntax checks.",
            "Do not physically move large code blocks until the app is stable for several sessions.",
        ],
        "next_action": "Use the Dashboard Structure Guide before making further UI changes.",
    }
