"""
AUTHOR: Rohan Joseph
PURPOSE: Test the shared validation guards that fail fast when a required column is missing or a
         required input file or directory is absent.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-08-04
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys
import pytest
import subprocess

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import settings, validation
from src.logger import capture_script_console_to_markdown



# ============================================================
# Tests
# ============================================================

def test_require_columns_raises_on_missing():
    """
    Check that require_columns raises a ValidationError when a required column is absent.
    This makes a stage stop early on malformed raw postings.
    """

    frame = pd.DataFrame({"id": ["1"]})

    with pytest.raises(validation.ValidationError):
        validation.require_columns(frame, ["id", "company_name"], context = "raw postings")


def test_require_existing_file_raises_on_missing():
    """
    Check that require_existing_file raises when the path does not exist.
    This turns a missing sample into an actionable error before a stage reads it.
    """

    missing_file = os.path.join(settings.INPUT_DIR, "does_not_exist.csv")

    with pytest.raises(validation.ValidationError):
        validation.require_existing_file(missing_file, context = "employer dictionary")


def test_require_existing_directory_raises_on_missing():
    """
    Check that require_existing_directory raises when the folder does not exist.
    This turns a missing raw Lightcast folder into an actionable error before scanning.
    """

    missing_dir = os.path.join(settings.INPUT_DIR, "does_not_exist_dir")

    with pytest.raises(validation.ValidationError):
        validation.require_existing_directory(missing_dir, context = "Lightcast folder")



# ============================================================
# Main Execution
# ============================================================

def main():
    """
    Run this test module through pytest in a subprocess and echo its output.
    This logs the test run like a pipeline script without the tee fighting pytest's capture.
    """

    command = [sys.executable, "-m", "pytest", __file__, "-v"]
    result = subprocess.run(command, capture_output = True, text = True)

    print(result.stdout, end = "")
    print(result.stderr, end = "")


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "t007_validation",
        log_dir = settings.LOG_DIR,
    )
