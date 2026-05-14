
from pathlib import Path
import subprocess
import sys
from datetime import datetime
import logging
import shutil


PROJECT_PATH = Path(r"C:\\Users\\yemi\\OneDrive\\Desktop\\quant_trading_project")
RUNS_PATH = PROJECT_PATH / "runs"

RUNS_PATH.mkdir(parents=True, exist_ok=True)


def create_run_folders():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    run_path = RUNS_PATH / timestamp
    results_path = run_path / "results"
    charts_path = run_path / "charts"
    logs_path = run_path / "logs"

    results_path.mkdir(parents=True, exist_ok=True)
    charts_path.mkdir(parents=True, exist_ok=True)
    logs_path.mkdir(parents=True, exist_ok=True)

    return run_path, results_path, charts_path, logs_path


def save_config_snapshot(run_path):
    config_file = PROJECT_PATH / "config.py"
    config_snapshot_file = run_path / "config_snapshot.py"

    if not config_file.exists():
        raise FileNotFoundError(f"Could not find config file: {config_file}")

    shutil.copy2(config_file, config_snapshot_file)

    return config_snapshot_file


def setup_logger(logs_path):
    log_file = logs_path / "research_pipeline.log"

    logger = logging.getLogger("quant_research_pipeline")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger, log_file


def run_script(script_name, logger, extra_args=None):
    if extra_args is None:
        extra_args = []

    script_path = PROJECT_PATH / script_name

    if not script_path.exists():
        logger.error(f"Could not find script: {script_path}")
        raise FileNotFoundError(f"Could not find script: {script_path}")

    logger.info("=" * 60)
    logger.info(f"Running script: {script_name}")
    logger.info("=" * 60)

    command = [sys.executable, str(script_path)] + extra_args

    logger.info(f"Command: {' '.join(command)}")

    result = subprocess.run(
        command,
        cwd=str(PROJECT_PATH),
        capture_output=True,
        text=True
    )

    if result.stdout:
        logger.info("Script output:")
        logger.info(result.stdout)

    if result.stderr:
        logger.warning("Script warnings/errors:")
        logger.warning(result.stderr)

    if result.returncode != 0:
        logger.error(f"{script_name} failed with exit code {result.returncode}")
        raise RuntimeError(f"{script_name} failed with exit code {result.returncode}")

    logger.info(f"Completed script successfully: {script_name}")


def run_pipeline():
    run_path, results_path, charts_path, logs_path = create_run_folders()
    logger, log_file = setup_logger(logs_path)

    logger.info("QUANT RESEARCH PIPELINE STARTED")
    logger.info(f"Project path: {PROJECT_PATH}")
    logger.info(f"Run path: {run_path}")
    logger.info(f"Results path: {results_path}")
    logger.info(f"Charts path: {charts_path}")
    logger.info(f"Logs path: {logs_path}")
    logger.info(f"Log file: {log_file}")

    try:
        config_snapshot_file = save_config_snapshot(run_path)
        logger.info(f"Config snapshot saved to: {config_snapshot_file}")

        run_script(
            "run_batch_tests.py",
            logger,
            extra_args=["--results-path", str(results_path)]
        )

        run_script(
            "generate_charts.py",
            logger,
            extra_args=[
                "--results-path", str(results_path),
                "--charts-path", str(charts_path),
                "--top-n", "3"
            ]
        )

        run_script(
            "walk_forward_test.py",
            logger,
            extra_args=["--results-path", str(results_path)]
        )

        logger.info("=" * 60)
        logger.info("QUANT RESEARCH PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"All files saved under: {run_path}")
        logger.info("=" * 60)

    except Exception as e:
        logger.exception("QUANT RESEARCH PIPELINE FAILED")
        raise e

    finally:
        logger.info("Pipeline finished.")


if __name__ == "__main__":
    run_pipeline()
