"""
AUTHOR: Rohan Joseph
PURPOSE: Validate runtime prerequisites for the repository.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
import sys



"""
Settings
"""

# --- Ensure that the src directory is on PATH ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# --- Import project-specific utilities and pipeline code ---
from project.env import get_runtime_config  # type: ignore
from project.paths import ensure_project_directories  # type: ignore
from project.logger import capture_script_console_to_markdown  # type: ignore



"""
Script
"""

def main() -> None:
    """
    Validate Python version, directories, and configured input paths.
    This helps fail early before expensive pipeline stages begin.
    """

    config = get_runtime_config()
    ensure_project_directories()

    checks_passed = True

    print("\nEnvironment validation\n")
    print(f"  - Python executable: {sys.executable}")
    print(f"  - Python version: {sys.version.split()[0]}")

    if sys.version_info < (3, 9, 6):
        print("  - ERROR: Python 3.9.6 or newer is required.")
        checks_passed = False

    if config.raw_lightcast_dir is None:
        print("  - ERROR: RAW_LIGHTCAST_DIR is not configured.")
        checks_passed = False
    elif not os.path.exists(config.raw_lightcast_dir):
        print(f"  - ERROR: RAW_LIGHTCAST_DIR does not exist: {config.raw_lightcast_dir}")
        checks_passed = False
    else:
        print(f"  - OK: RAW_LIGHTCAST_DIR exists: {config.raw_lightcast_dir}")

    if config.employer_job_postings_path is None:
        print("  - WARNING: EMPLOYER_JOB_POSTINGS_PATH is not configured. Stage 3 will not run.")
    elif not os.path.exists(config.employer_job_postings_path):
        print(f"  - ERROR: EMPLOYER_JOB_POSTINGS_PATH does not exist: {config.employer_job_postings_path}")
        checks_passed = False
    else:
        print(f"  - OK: EMPLOYER_JOB_POSTINGS_PATH exists: {config.employer_job_postings_path}")

    print(f"  - Runtime mode: {config.runtime_mode}")
    print(f"  - Employer match threshold: {config.employer_match_threshold}")
    print(f"  - Chunk size: {config.chunk_size}")

    if not checks_passed:
        raise SystemExit(1)

    print("\nEnvironment checks passed.")



"""
Main Execution
"""

if __name__ == "__main__":
    log_path = capture_script_console_to_markdown(
        run_callable = main,
        output_dir = os.path.join(PROJECT_ROOT, "output", "logs"),
        script_name = "check_env",
        also_print_to_console = True,
    )
    print(f"Saved run log to: {log_path}")