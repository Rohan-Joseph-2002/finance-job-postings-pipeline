"""
AUTHOR: Rohan Joseph
PURPOSE: Test employer matching — an exact standardized-name match, an unmatched source employer,
         and the token-aware name similarity used for the fuzzy fallback.
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
from src.matching import compute_name_similarity, match_standardized_employers



# ============================================================
# Tests
# ============================================================

def source_frame():
    """
    Build a source employer frame with one reference-aligned name and one unknown name.
    This drives both the matched and unmatched outcomes of the matcher.
    """

    return pd.DataFrame(
        {
            "company": [1001, 1002],
            "company_name": ["North Shore Capital LLC", "Obscure Startup Inc"],
            "job_posting_count": [3, 1],
            "company_name_standardized": ["north shore capital", "obscure startup"],
        }
    )


def reference_frame():
    """
    Build a one-employer standardized reference frame with a relevance percentage.
    This gives the matcher a reference row to resolve the source employer against.
    """

    return pd.DataFrame(
        {
            "company": [2001],
            "company_name": ["North Shore Capital"],
            "job_posting_count": [10],
            "company_name_standardized": ["north shore capital"],
            "percentage_relevant_jobs": [0.95],
        }
    )


def test_match_standardized_employers_exact_and_unmatched():
    """
    Check that an aligned name matches exactly and an unknown name is left unmatched.
    This confirms the exact-then-fuzzy matcher splits sources into the two output tables.
    """

    matched_df, unmatched_df = match_standardized_employers(
        source_employers_df = source_frame(),
        reference_employers_df = reference_frame(),
        threshold = 0.92,
    )

    assert matched_df["match_method"].tolist() == ["exact_standardized_name"]
    assert matched_df.loc[0, "percentage_relevant_jobs"] == 0.95
    assert unmatched_df["source_company_name"].tolist() == ["Obscure Startup Inc"]


def test_compute_name_similarity_is_one_for_identical_names():
    """
    Check that two identical standardized names score a perfect similarity.
    This anchors the fuzzy fallback scoring used when no exact match exists.
    """

    assert compute_name_similarity("north shore capital", "north shore capital") == 1.0



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
        script_name = "t004_employer_matching",
        log_dir = settings.LOG_DIR,
    )
