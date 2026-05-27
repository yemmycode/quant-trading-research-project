
"""
Automated Test Runner

This module runs selected local test scripts and reports pass/fail status.

It does not run dangerous broker execution tests by default.
It does not place orders.
It does not enable live trading.
"""

from pathlib import Path
from datetime import datetime
import subprocess
import sys
import pandas as pd

from trading_database import (
    initialize_trading_database,
    get_database_connection,
    safe_json
)


PROJECT_PATH = Path(__file__).resolve().parent


SAFE_TEST_SCRIPTS = [
    "test_trading_database.py",
    "test_order_state_manager.py",
    "test_duplicate_order_guard.py",
    "test_position_aware_execution.py",
    "test_snapshot_position_aware_execution.py",
    "test_broker_account_snapshot.py",
    "test_market_hours.py",
    "test_price_validation.py",
    "test_fill_slippage_tracker.py",
    "test_error_notifier.py",
    "test_system_health.py",
    "test_deployment_health.py",
    "test_secure_broker_architecture.py",
]


BROKER_TEST_SCRIPTS = [
    "test_ibkr_connection.py",
    "test_ibkr_account_info.py",
    "test_ibkr_positions.py",
    "test_ibkr_market_data.py",
    "test_ibkr_live_read_only.py",
]


def initialize_test_runner_tables():
    """
    Create test runner results table.
    """

    initialize_trading_database()

    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_run_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            test_script TEXT NOT NULL,
            test_group TEXT,
            passed INTEGER NOT NULL,
            return_code INTEGER,
            duration_seconds REAL,
            stdout_text TEXT,
            stderr_text TEXT,
            raw_result_json TEXT
        )
    """)

    conn.commit()
    conn.close()

    return True


def list_available_tests(include_broker_tests=False):
    """
    List available test scripts.
    """

    scripts = list(SAFE_TEST_SCRIPTS)

    if include_broker_tests:
        scripts += BROKER_TEST_SCRIPTS

    rows = []

    for script in scripts:
        script_path = PROJECT_PATH / script

        rows.append({
            "test_script": script,
            "exists": script_path.exists(),
            "path": str(script_path),
            "group": "broker" if script in BROKER_TEST_SCRIPTS else "safe",
        })

    return rows


def run_single_test_script(test_script, timeout_seconds=120):
    """
    Run one test script and capture output.
    """

    initialize_test_runner_tables()

    if test_script not in SAFE_TEST_SCRIPTS and test_script not in BROKER_TEST_SCRIPTS:
        raise ValueError(f"Unsupported test script: {test_script}")

    script_path = PROJECT_PATH / test_script

    if not script_path.exists():
        result = {
            "test_script": test_script,
            "test_group": "broker" if test_script in BROKER_TEST_SCRIPTS else "safe",
            "passed": False,
            "return_code": None,
            "duration_seconds": 0.0,
            "stdout_text": "",
            "stderr_text": f"Test script not found: {script_path}",
        }

        save_test_result(result)
        return result

    start_time = datetime.now()

    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_PATH),
            capture_output=True,
            text=True,
            timeout=int(timeout_seconds),
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = {
            "test_script": test_script,
            "test_group": "broker" if test_script in BROKER_TEST_SCRIPTS else "safe",
            "passed": completed.returncode == 0,
            "return_code": completed.returncode,
            "duration_seconds": duration,
            "stdout_text": completed.stdout,
            "stderr_text": completed.stderr,
        }

    except subprocess.TimeoutExpired as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = {
            "test_script": test_script,
            "test_group": "broker" if test_script in BROKER_TEST_SCRIPTS else "safe",
            "passed": False,
            "return_code": None,
            "duration_seconds": duration,
            "stdout_text": e.stdout or "",
            "stderr_text": f"TimeoutExpired: test exceeded {timeout_seconds} seconds.",
        }

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = {
            "test_script": test_script,
            "test_group": "broker" if test_script in BROKER_TEST_SCRIPTS else "safe",
            "passed": False,
            "return_code": None,
            "duration_seconds": duration,
            "stdout_text": "",
            "stderr_text": f"{type(e).__name__}: {e}",
        }

    save_test_result(result)
    return result


def save_test_result(result):
    """
    Save test result to database.
    """

    initialize_test_runner_tables()

    conn = get_database_connection()
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO test_run_results (
            created_at,
            test_script,
            test_group,
            passed,
            return_code,
            duration_seconds,
            stdout_text,
            stderr_text,
            raw_result_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            now,
            result.get("test_script"),
            result.get("test_group"),
            1 if result.get("passed") else 0,
            result.get("return_code"),
            result.get("duration_seconds"),
            result.get("stdout_text"),
            result.get("stderr_text"),
            safe_json(result),
        )
    )

    test_result_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return test_result_id


def run_selected_tests(test_scripts, timeout_seconds=120):
    """
    Run selected test scripts.
    """

    results = []

    for script in test_scripts:
        result = run_single_test_script(
            test_script=script,
            timeout_seconds=timeout_seconds
        )
        results.append(result)

    return results


def run_safe_test_suite(timeout_seconds=120):
    """
    Run the safe non-broker test suite.
    """

    available = list_available_tests(include_broker_tests=False)

    existing_scripts = [
        row["test_script"]
        for row in available
        if row["exists"]
    ]

    return run_selected_tests(
        test_scripts=existing_scripts,
        timeout_seconds=timeout_seconds
    )


def read_test_results(limit=100):
    """
    Read recent test results.
    """

    initialize_test_runner_tables()

    conn = get_database_connection()

    query = """
        SELECT *
        FROM test_run_results
        ORDER BY id DESC
        LIMIT ?
    """

    df = pd.read_sql_query(query, conn, params=(int(limit),))
    conn.close()

    return df


def summarize_test_results(limit=100):
    """
    Summarize recent test results.
    """

    df = read_test_results(limit=limit)

    if df.empty:
        return {
            "has_data": False,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "pass_rate": 0.0,
            "message": "No test results found.",
        }

    total_tests = len(df)
    passed_tests = int(df["passed"].sum())
    failed_tests = total_tests - passed_tests
    pass_rate = passed_tests / total_tests if total_tests else 0.0

    latest_by_script = (
        df.sort_values("id", ascending=False)
        .drop_duplicates(subset=["test_script"], keep="first")
    )

    latest_total = len(latest_by_script)
    latest_passed = int(latest_by_script["passed"].sum())
    latest_failed = latest_total - latest_passed
    latest_pass_rate = latest_passed / latest_total if latest_total else 0.0

    return {
        "has_data": True,
        "total_test_runs": int(total_tests),
        "passed_test_runs": int(passed_tests),
        "failed_test_runs": int(failed_tests),
        "pass_rate": round(pass_rate, 4),
        "latest_unique_tests": int(latest_total),
        "latest_passed": int(latest_passed),
        "latest_failed": int(latest_failed),
        "latest_pass_rate": round(latest_pass_rate, 4),
    }


def get_test_runner_status():
    """
    Return test runner status.
    """

    initialize_test_runner_tables()

    available_safe = list_available_tests(include_broker_tests=False)
    available_all = list_available_tests(include_broker_tests=True)
    summary = summarize_test_results(limit=500)

    return {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "safe_tests_count": len(available_safe),
        "all_tests_count": len(available_all),
        "available_safe_tests": available_safe,
        "available_all_tests": available_all,
        "summary": summary,
        "purpose": "Run safe local test scripts and review pass/fail results.",
    }
