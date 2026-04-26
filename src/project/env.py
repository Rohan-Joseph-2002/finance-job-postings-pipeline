"""
AUTHOR: Rohan Joseph
PURPOSE: Environment loading and runtime configuration validation.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""

from __future__ import annotations



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
from dataclasses import dataclass


# --- Import project-specific utilities and pipeline code ---
from project.paths import PROJECT_ROOT
from project.settings import (
    EMPLOYER_MATCH_THRESHOLD_DEFAULT,
    EMPLOYER_RELEVANCE_THRESHOLD_DEFAULT,
)



"""
Settings
"""

ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
DEFAULT_RAW_LIGHTCAST_DIR = os.path.join("input", "lightcast_sample")
DEFAULT_EMPLOYER_JOB_POSTINGS_PATH = os.path.join(
    "input",
    "reference",
    "Sample Set - Lightcast Employer-Job Postings Dictionary.csv",
)



"""
Classes
"""

@dataclass(frozen = True)
class RuntimeConfig:
    """
    Typed runtime configuration for the repository.
    This gives the rest of the repository one typed source of runtime settings and paths.
    """

    runtime_mode: str
    raw_lightcast_dir: str | None
    employer_job_postings_path: str | None
    employer_relevance_threshold: float
    employer_match_threshold: float
    chunk_size: int



"""
Functions
"""

def load_dotenv_file(env_path: str = ENV_FILE) -> None:
    """
    Load key-value pairs from a local .env file into the process environment.
    This helps keep the repository self-contained without requiring external dotenv packages.
    """

    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding = "utf-8") as handle:
        raw_lines = handle.readlines()

    for raw_line in raw_lines:
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key and key not in os.environ:
            # Respect any variables the caller already supplied while still honoring repo-local defaults.
            os.environ[key] = value


def resolve_project_path(path_value: str | None, default_path: str | None = None) -> str | None:
    """
    Resolve a configured path relative to the project root when needed.
    This helps support portable local defaults without forcing absolute paths in .env files.
    """

    if path_value is None:
        if default_path is None:
            return None
        return os.path.abspath(os.path.join(PROJECT_ROOT, default_path))

    candidate_path = os.path.expanduser(path_value)

    if os.path.isabs(candidate_path):
        return os.path.abspath(candidate_path)

    return os.path.abspath(os.path.join(PROJECT_ROOT, candidate_path))


def get_runtime_config() -> RuntimeConfig:
    """
    Build the runtime configuration from environment variables and .env.
    This helps standardize path handling and stage behavior across entry scripts.
    """

    load_dotenv_file()

    # Assemble one typed config object so every script resolves paths and thresholds the same way.
    return RuntimeConfig(
        runtime_mode = os.environ.get("RUNTIME_MODE", "local"),
        raw_lightcast_dir = resolve_project_path(
            path_value = os.environ.get("RAW_LIGHTCAST_DIR"),
            default_path = DEFAULT_RAW_LIGHTCAST_DIR,
        ),
        employer_job_postings_path = resolve_project_path(
            path_value = os.environ.get("EMPLOYER_JOB_POSTINGS_PATH"),
            default_path = DEFAULT_EMPLOYER_JOB_POSTINGS_PATH,
        ),
        employer_relevance_threshold = float(
            os.environ.get("EMPLOYER_RELEVANCE_THRESHOLD", EMPLOYER_RELEVANCE_THRESHOLD_DEFAULT)
        ),
        employer_match_threshold = float(
            os.environ.get("EMPLOYER_MATCH_THRESHOLD", EMPLOYER_MATCH_THRESHOLD_DEFAULT)
        ),
        chunk_size = int(os.environ.get("CHUNK_SIZE", "50000")),
    )
