"""
AUTHOR: Rohan Joseph
PURPOSE: Test employer name standardization and the standardized employer-frame builder that folds
         suffixes and generic words and counts postings per employer.
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
from src.matching import build_employer_standardization_frame, standardize_employer_name



# ============================================================
# Tests
# ============================================================

def test_standardize_employer_name_folds_suffixes_and_generic_words():
    """
    Check that a leading "the", legal suffixes, and a generic trailing word are all folded.
    This is the normalization that lets differently written employer names align.
    """

    assert standardize_employer_name("The Goldman Sachs Group Inc") == "goldman sachs"
    assert standardize_employer_name("North Shore Capital LLC") == "north shore capital"


def test_build_employer_standardization_frame_counts_postings():
    """
    Check that the employer frame counts postings per employer and sorts by count.
    This gives the matching stage one row per employer with a posting weight.
    """

    df = pd.DataFrame(
        {
            "company": [1, 1, 2],
            "company_name": ["Goldman Sachs Inc", "Goldman Sachs Inc", "Union Crest Bank Inc"],
        }
    )

    standardized_df = build_employer_standardization_frame(df)

    assert standardized_df["job_posting_count"].tolist() == [2, 1]
    assert standardized_df.loc[0, "company_name_standardized"] == "goldman sachs"



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
        script_name = "t003_employer_standardization",
        log_dir = settings.LOG_DIR,
    )
