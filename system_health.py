
"""
System Health Check

This module checks whether key project modules, files, logs, and safety systems
are available and functioning.

It does not connect to IBKR.
It does not place orders.
It does not enable live trading.
"""

from pathlib import Path
from datetime import datetime
import importlib
import pandas as pd


PROJECT_PATH = Path(__file__).resolve().parent


REQUIRED_FILES = [
    "app.py",
    "config.py",
    "risk_manager.py",
    "safety_manager.py",
    "trade_audit.py",
    "paper_test_tracker.py",
    "live_readiness.py",
    "live_mode_lock.py",
    "live_warning.py",
    "live_order_dry_run.py",
    "broker_environment.py",
    "environment_reset.py",
    "order_proposal.py",
    "live_signal.py",
    "requirements.txt",
]


REQUIRED_FOLDERS = [
    "brokers",
    "strategies",
]


REQUIRED_MODULES = [
    "config",
    "risk_manager",
    "safety_manager",
    "trade_audit",
    "paper_test_tracker",
    "live_readiness",
    "live_mode_lock",
    "live_warning",
    "live_order_dry_run",
    "broker_environment",
    "environment_reset",
    "order_proposal",
    "live_signal",
]


def check_required_files():
    rows = []

    for file_name in REQUIRED_FILES:
        file_path = PROJECT_PATH / file_name

        rows.append({
            "item": file_name,
            "type": "file",
            "exists": file_path.exists(),
            "path": str(file_path)
        })

    return rows


def check_required_folders():
    rows = []

    for folder_name in REQUIRED_FOLDERS:
        folder_path = PROJECT_PATH / folder_name

        rows.append({
            "item": folder_name,
            "type": "folder",
            "exists": folder_path.exists(),
            "path": str(folder_path)
        })

    return rows


def check_module_imports():
    rows = []

    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)

            rows.append({
                "module": module_name,
                "import_ok": True,
                "error": ""
            })

        except Exception as e:
            rows.append({
                "module": module_name,
                "import_ok": False,
                "error": f"{type(e).__name__}: {e}"
            })

    return rows


def check_config_safety():
    try:
        from config import (
            EXECUTION_MODE,
            DEFAULT_BROKER,
            ALLOW_LIVE_TRADING,
            LIVE_TRADING_ENABLED,
            REQUIRE_MANUAL_CONFIRMATION,
            IBKR_TRADING_MODE,
            IBKR_READ_ONLY,
            IBKR_ENABLE_ORDERS
        )

        warnings = []
        blockers = []

        if ALLOW_LIVE_TRADING:
            blockers.append("ALLOW_LIVE_TRADING is True.")

        if LIVE_TRADING_ENABLED:
            blockers.append("LIVE_TRADING_ENABLED is True.")

        if not REQUIRE_MANUAL_CONFIRMATION:
            blockers.append("REQUIRE_MANUAL_CONFIRMATION is False.")

        if IBKR_TRADING_MODE == "live" and not IBKR_READ_ONLY:
            blockers.append("IBKR live mode is not read-only.")

        if IBKR_TRADING_MODE == "live" and IBKR_ENABLE_ORDERS:
            blockers.append("IBKR live mode has orders enabled.")

        if IBKR_TRADING_MODE == "paper" and IBKR_ENABLE_ORDERS:
            warnings.append("IBKR paper order testing is enabled.")

        safe = len(blockers) == 0

        return {
            "check": "config_safety",
            "ok": safe,
            "warnings": warnings,
            "blockers": blockers,
            "snapshot": {
                "EXECUTION_MODE": EXECUTION_MODE,
                "DEFAULT_BROKER": DEFAULT_BROKER,
                "ALLOW_LIVE_TRADING": ALLOW_LIVE_TRADING,
                "LIVE_TRADING_ENABLED": LIVE_TRADING_ENABLED,
                "REQUIRE_MANUAL_CONFIRMATION": REQUIRE_MANUAL_CONFIRMATION,
                "IBKR_TRADING_MODE": IBKR_TRADING_MODE,
                "IBKR_READ_ONLY": IBKR_READ_ONLY,
                "IBKR_ENABLE_ORDERS": IBKR_ENABLE_ORDERS,
            }
        }

    except Exception as e:
        return {
            "check": "config_safety",
            "ok": False,
            "warnings": [],
            "blockers": [f"Could not read config safely: {type(e).__name__}: {e}"],
            "snapshot": {}
        }


def check_safety_systems():
    results = {}

    try:
        from safety_manager import read_emergency_stop_state
        results["emergency_stop"] = {
            "ok": True,
            "state": read_emergency_stop_state()
        }
    except Exception as e:
        results["emergency_stop"] = {
            "ok": False,
            "error": f"{type(e).__name__}: {e}"
        }

    try:
        from live_warning import read_warning_state
        results["live_warning"] = {
            "ok": True,
            "state": read_warning_state()
        }
    except Exception as e:
        results["live_warning"] = {
            "ok": False,
            "error": f"{type(e).__name__}: {e}"
        }

    try:
        from live_mode_lock import evaluate_live_mode_lock
        results["live_mode_lock"] = {
            "ok": True,
            "state": evaluate_live_mode_lock()
        }
    except Exception as e:
        results["live_mode_lock"] = {
            "ok": False,
            "error": f"{type(e).__name__}: {e}"
        }

    try:
        from broker_environment import get_environment_recommendation
        results["broker_environment"] = {
            "ok": True,
            "state": get_environment_recommendation()
        }
    except Exception as e:
        results["broker_environment"] = {
            "ok": False,
            "error": f"{type(e).__name__}: {e}"
        }

    return results


def check_logs():
    log_paths = {
        "trade_audit_log": PROJECT_PATH / "logs" / "trade_audit_log.csv",
        "paper_test_log": PROJECT_PATH / "paper_test" / "paper_trading_30_day_log.csv",
        "daily_report": PROJECT_PATH / "paper_test" / "daily_paper_trading_report.csv",
        "weekly_review": PROJECT_PATH / "paper_test" / "weekly_paper_trading_review.csv",
    }

    rows = []

    for name, path in log_paths.items():
        exists = path.exists()

        row = {
            "log_name": name,
            "exists": exists,
            "path": str(path),
            "rows": 0,
            "error": ""
        }

        if exists:
            try:
                df = pd.read_csv(path)
                row["rows"] = len(df)
            except Exception as e:
                row["error"] = f"{type(e).__name__}: {e}"

        rows.append(row)

    return rows


def run_system_health_check():
    file_rows = check_required_files()
    folder_rows = check_required_folders()
    module_rows = check_module_imports()
    config_safety = check_config_safety()
    safety_systems = check_safety_systems()
    log_rows = check_logs()

    files_ok = all(row["exists"] for row in file_rows)
    folders_ok = all(row["exists"] for row in folder_rows)
    modules_ok = all(row["import_ok"] for row in module_rows)
    config_ok = config_safety.get("ok", False)
    safety_ok = all(item.get("ok", False) for item in safety_systems.values())

    overall_ok = files_ok and folders_ok and modules_ok and config_ok and safety_ok

    if overall_ok:
        status = "healthy"
        recommendation = "Core system checks passed. Continue controlled paper validation."
    elif modules_ok and safety_ok:
        status = "warning"
        recommendation = "Core modules and safety systems are available, but review missing files/config warnings."
    else:
        status = "needs_attention"
        recommendation = "One or more critical checks failed. Fix these before broker testing."

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_ok": overall_ok,
        "status": status,
        "recommendation": recommendation,
        "summary": {
            "files_ok": files_ok,
            "folders_ok": folders_ok,
            "modules_ok": modules_ok,
            "config_ok": config_ok,
            "safety_ok": safety_ok,
        },
        "files": file_rows,
        "folders": folder_rows,
        "modules": module_rows,
        "config_safety": config_safety,
        "safety_systems": safety_systems,
        "logs": log_rows,
    }
