"""
AUTHOR: Rohan Joseph
PURPOSE: Test the Stage 5 employer filter — that finance jobs are kept only when their standardized
         employer matched the reference list, joining on the standardized name.
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
from data.d005_employer_filtered_finance_jobs import filter_jobs_to_matched_employers



# ============================================================
# Tests
# ============================================================

def test_filter_jobs_keeps_only_matched_employers():
    """
    Check that only jobs whose standardized employer matched the reference are kept.
    This confirms the stage restricts the sample to reference-linked employers.
    """

    finance_jobs_df = pd.DataFrame(
        {
            "id": [1, 2],
            "company_name": ["Goldman Sachs Inc", "Acme Widgets Inc"],
        }
    )
    matched_employers_df = pd.DataFrame(
        {
            "source_company_name_standardized": ["goldman sachs"],
            "reference_company_name": ["The Goldman Sachs Group Inc"],
            "percentage_relevant_jobs": [0.85],
        }
    )

    filtered_df = filter_jobs_to_matched_employers(finance_jobs_df, matched_employers_df)

    assert filtered_df["id"].tolist() == [1]
    assert filtered_df.loc[0, "reference_company_name"] == "The Goldman Sachs Group Inc"



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
        script_name = "t005_employer_filtered_finance_jobs",
        log_dir = settings.LOG_DIR,
    )
