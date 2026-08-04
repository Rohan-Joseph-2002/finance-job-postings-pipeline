"""
AUTHOR: Rohan Joseph
PURPOSE: Test the Stage 2 finance selection — keeping only jobs that appear in at least two of the
         four inclusion signals — and the shared keyword-containment helper.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-08-04
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys
import subprocess

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import settings
from src.logger import capture_script_console_to_markdown
from data.d002_finance_related_jobs import contains_any_keyword, filter_finance_related_jobs



# ============================================================
# Tests
# ============================================================

def test_filter_finance_related_jobs_requires_two_signals():
    """
    Check that a two-signal job is kept while a single-signal job is dropped.
    This confirms finance selection does not rely on any single taxonomy field.
    """

    df = pd.DataFrame(
        {
            "id": [1, 2],
            "naics2_name": ["Finance and Insurance", "Finance and Insurance"],
            "cip6_name": ["", ""],
            "skills_name": ["", ""],
            "title_clean": ["Financial Analyst", "Office Manager"],
        }
    )

    finance_df = filter_finance_related_jobs(df)

    assert finance_df["id"].tolist() == [1]


def test_contains_any_keyword_matches_substring():
    """
    Check that keyword containment matches case-insensitively on a substring.
    This underpins the CIP, skills, and title inclusion filters.
    """

    assert contains_any_keyword("Financial Analyst", settings.TITLE_KEEP_KEYWORDS) is True
    assert contains_any_keyword("Office Manager", settings.FINANCE_KEYWORDS) is False



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
        script_name = "t002_finance_related_jobs",
        log_dir = settings.LOG_DIR,
    )
