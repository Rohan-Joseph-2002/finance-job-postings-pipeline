"""
AUTHOR: Rohan Joseph
PURPOSE: Tests for repository environment bootstrapping helpers.
DATE CREATED: 2026-04-26
DATE MODIFIED: 2026-04-26
MODIFIED BY: Codex
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
from pathlib import Path


# --- Import project-specific utilities and pipeline code ---
from scripts.setup_env import ensure_env_file



"""
Tests
"""


def test_ensure_env_file_creates_env_from_example(tmp_path):
    """
    Test that setup_env creates a repo-local .env from .env.example when one is missing.
    This helps lock in the expected bootstrap behavior for first-run setup.
    """

    project_root = Path(tmp_path)
    env_example_path = project_root / ".env.example"
    env_path = project_root / ".env"

    env_example_path.write_text("RUNTIME_MODE=local\nCHUNK_SIZE=123\n", encoding = "utf-8")

    created_env_path = ensure_env_file(str(project_root))

    assert created_env_path == str(env_path)
    assert env_path.read_text(encoding = "utf-8") == env_example_path.read_text(encoding = "utf-8")


def test_ensure_env_file_preserves_existing_env(tmp_path):
    """
    Test that setup_env keeps an existing repo-local .env instead of overwriting it.
    This helps protect local machine-specific configuration during repeated setup runs.
    """

    project_root = Path(tmp_path)
    env_example_path = project_root / ".env.example"
    env_path = project_root / ".env"

    env_example_path.write_text("CHUNK_SIZE=123\n", encoding = "utf-8")
    env_path.write_text("CHUNK_SIZE=999\n", encoding = "utf-8")

    created_env_path = ensure_env_file(str(project_root))

    assert created_env_path == str(env_path)
    assert env_path.read_text(encoding = "utf-8") == "CHUNK_SIZE=999\n"
