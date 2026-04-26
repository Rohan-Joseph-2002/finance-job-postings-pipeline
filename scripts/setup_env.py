"""
AUTHOR: Rohan Joseph
PURPOSE: Set up the local repository environment and expected directory structure.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-26
MODIFIED BY: Codex
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
import argparse
import shutil
import subprocess
import sys
import venv




"""
Settings
"""

# --- Ensure that the src directory is on PATH ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


# --- Import project-specific utilities and pipeline code ---
from project.paths import ensure_project_directories  # type: ignore
from project.paths import PROJECT_ROOT as PACKAGE_PROJECT_ROOT  # type: ignore
from project.logger import capture_script_console_to_markdown  # type: ignore



"""
Script
"""

def resolve_python_path(project_root: str) -> str:
    """
    Resolve the Python interpreter that should be used for dependency installation.
    This helps target the local virtual environment when it exists and otherwise fall back to the current interpreter.
    """

    venv_python_path = os.path.join(project_root, ".venv", "bin", "python")

    if os.path.exists(venv_python_path):
        return venv_python_path

    return sys.executable


def install_requirements(python_path: str, project_root: str) -> None:
    """
    Install the repository requirements using the selected interpreter.
    This helps ensure the local environment has the packages needed to run the pipeline and unit tests.
    """

    requirements_path = os.path.join(project_root, "requirements.txt")

    print(f"Installing requirements from: {requirements_path}")
    subprocess.run(
        [python_path, "-m", "pip", "install", "-r", requirements_path],
        cwd = project_root,
        check = True,
    )


def ensure_env_file(project_root: str) -> str:
    """
    Create a repo-local .env from .env.example when needed.
    This helps first-run setup succeed with a tracked configuration template while preserving local overrides.
    """

    env_example_path = os.path.join(project_root, ".env.example")
    env_path = os.path.join(project_root, ".env")

    if os.path.exists(env_path):
        print(f"Using existing environment file: {env_path}")
        return env_path

    if not os.path.exists(env_example_path):
        raise FileNotFoundError(
            f"Missing environment template: {env_example_path}. Add .env.example before running setup."
        )

    shutil.copyfile(env_example_path, env_path)
    print(f"Created environment file from template: {env_path}")
    return env_path


def main() -> None:
    """
    Create the standard repository directories and optionally bootstrap a local virtual environment.
    This helps make first-run setup deterministic and fully Python-driven.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--create-venv", action = "store_true")
    parser.add_argument("--install-project", action = "store_true")
    args = parser.parse_args()

    print(f"Project root: {PACKAGE_PROJECT_ROOT}")
    paths = ensure_project_directories()
    ensure_env_file(PROJECT_ROOT)

    print("Created or verified standard directories:")
    print(f"  - {paths.stage_001_dir}")
    print(f"  - {paths.stage_002_dir}")
    print(f"  - {paths.stage_003_dir}")
    print(f"  - {paths.stage_004_dir}")
    print(f"  - {paths.stage_005_dir}")
    print(f"  - {paths.stage_006_dir}")
    print(f"  - {paths.log_dir}")

    venv_path = os.path.join(PROJECT_ROOT, ".venv")

    if args.create_venv:
        print(f"Creating virtual environment at: {venv_path}")
        venv.EnvBuilder(with_pip = True).create(venv_path)

    python_path = resolve_python_path(PROJECT_ROOT)
    install_requirements(python_path = python_path, project_root = PROJECT_ROOT)

    if args.install_project:
        print(f"Installing project with interpreter: {python_path}")
        subprocess.run(
            [python_path, "-m", "pip", "install", "-e", "."],
            cwd = PROJECT_ROOT,
            check = True,
        )

    print("Environment setup completed.")



"""
Main Execution
"""

if __name__ == "__main__":
    log_path = capture_script_console_to_markdown(
        run_callable = main,
        output_dir = os.path.join(PROJECT_ROOT, "output", "logs"),
        script_name = "setup_env",
        also_print_to_console = True,
    )
    print(f"Saved run log to: {log_path}")
