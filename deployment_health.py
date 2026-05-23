
"""
Deployment Health Check

This module checks whether the app is running locally or on Streamlit Cloud,
and explains which features are safe/available in the current environment.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from pathlib import Path
from datetime import datetime
import os
import socket
import platform
import sys


PROJECT_PATH = Path(__file__).resolve().parent


def detect_runtime_environment():
    """
    Detect whether the app is likely running locally or on Streamlit Cloud.
    """

    env_vars = {
        "STREAMLIT_SHARING": os.getenv("STREAMLIT_SHARING"),
        "STREAMLIT_SERVER_HEADLESS": os.getenv("STREAMLIT_SERVER_HEADLESS"),
        "HOME": os.getenv("HOME"),
        "USER": os.getenv("USER"),
        "USERNAME": os.getenv("USERNAME"),
        "HOSTNAME": os.getenv("HOSTNAME"),
        "PYTHON_VERSION": sys.version.split()[0],
        "PLATFORM": platform.platform(),
    }

    project_path_text = str(PROJECT_PATH).lower()
    home_text = str(os.getenv("HOME", "")).lower()
    hostname_text = str(os.getenv("HOSTNAME", "")).lower()
    user_text = str(os.getenv("USER", "")).lower()

    streamlit_cloud_signals = [
        "/mount/src" in project_path_text,
        "appuser" in user_text,
        "streamlit" in hostname_text,
        "/home/adminuser" in project_path_text,
        "/home/appuser" in project_path_text,
    ]

    is_streamlit_cloud = any(streamlit_cloud_signals)

    if is_streamlit_cloud:
        environment = "STREAMLIT_CLOUD"
    else:
        environment = "LOCAL"

    return {
        "environment": environment,
        "is_streamlit_cloud": is_streamlit_cloud,
        "is_local": not is_streamlit_cloud,
        "project_path": str(PROJECT_PATH),
        "environment_variables": env_vars,
        "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def check_localhost_ibkr_availability():
    """
    Check whether localhost IBKR ports appear reachable.

    This is only a socket-level check.
    It does not authenticate.
    It does not place orders.
    """

    ports = {
        "tws_live_default_7496": 7496,
        "tws_paper_default_7497": 7497,
        "gateway_live_default_4001": 4001,
        "gateway_paper_default_4002": 4002,
    }

    results = []

    for name, port in ports.items():
        reachable = False
        error = ""

        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                reachable = True
        except Exception as e:
            error = f"{type(e).__name__}: {e}"

        results.append({
            "service": name,
            "host": "127.0.0.1",
            "port": port,
            "reachable": reachable,
            "error": error,
        })

    return results


def get_deployment_feature_matrix():
    """
    Return feature availability based on detected environment.
    """

    runtime = detect_runtime_environment()
    is_cloud = runtime["is_streamlit_cloud"]

    features = [
        {
            "feature": "Backtesting",
            "available": True,
            "environment_note": "Available locally and on Streamlit Cloud if dependencies/data sources are available."
        },
        {
            "feature": "Research pipeline",
            "available": True,
            "environment_note": "Available locally and on Streamlit Cloud, subject to file/data availability."
        },
        {
            "feature": "Live signal generation",
            "available": True,
            "environment_note": "Available if strategy modules and market data access work."
        },
        {
            "feature": "Order proposal builder",
            "available": True,
            "environment_note": "Available because it does not connect to broker."
        },
        {
            "feature": "Risk manager",
            "available": True,
            "environment_note": "Available locally and on Streamlit Cloud."
        },
        {
            "feature": "Emergency stop",
            "available": True,
            "environment_note": "Available, but Streamlit Cloud runtime state may reset across redeploys."
        },
        {
            "feature": "Trade audit log",
            "available": True,
            "environment_note": "Available, but Streamlit Cloud local files may not be permanent across redeploys."
        },
        {
            "feature": "IBKR paper order submission",
            "available": not is_cloud,
            "environment_note": (
                "Local only. Streamlit Cloud cannot reach your laptop TWS at 127.0.0.1."
                if is_cloud else
                "Available locally only if TWS/IB Gateway is open and API settings are correct."
            )
        },
        {
            "feature": "IBKR paper order cancellation",
            "available": not is_cloud,
            "environment_note": (
                "Local only. Streamlit Cloud cannot reach local TWS/IB Gateway."
                if is_cloud else
                "Available locally only if TWS/IB Gateway is open and orders are enabled for paper testing."
            )
        },
        {
            "feature": "IBKR live read-only check",
            "available": not is_cloud,
            "environment_note": (
                "Local only unless a secure server/VPS is running IB Gateway."
                if is_cloud else
                "Available locally only when TWS live is open with Read-Only API enabled."
            )
        },
        {
            "feature": "IBKR live order execution",
            "available": False,
            "environment_note": "Not enabled. Must remain blocked until readiness, warning, dry run, and live mode lock are complete."
        },
    ]

    return {
        "runtime": runtime,
        "features": features,
    }


def run_deployment_health_check():
    """
    Run deployment health diagnostics.
    """

    runtime = detect_runtime_environment()
    feature_matrix = get_deployment_feature_matrix()

    localhost_ibkr = []

    if runtime["is_local"]:
        localhost_ibkr = check_localhost_ibkr_availability()
    else:
        localhost_ibkr = [
            {
                "service": "ibkr_localhost_check_skipped",
                "host": "127.0.0.1",
                "port": None,
                "reachable": False,
                "error": "Skipped because Streamlit Cloud cannot access your local laptop localhost."
            }
        ]

    if runtime["is_streamlit_cloud"]:
        status = "cloud_safe_limited"
        recommendation = (
            "App is running on Streamlit Cloud. Use it for dashboards, reports, signals, and review. "
            "Do not expect IBKR TWS localhost connection to work here."
        )
    else:
        status = "local_runtime"
        recommendation = (
            "App is running locally. IBKR connectivity may work if TWS/IB Gateway is open and configured correctly."
        )

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "recommendation": recommendation,
        "runtime": runtime,
        "localhost_ibkr": localhost_ibkr,
        "feature_matrix": feature_matrix["features"],
    }
