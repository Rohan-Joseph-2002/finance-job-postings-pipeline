"""
AUTHOR: Rohan Joseph
PURPOSE: Test the Analysis 1 summary builders — per-dataset row and employer counts, and the
         cross-dataset employer-overlap comparison.
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
from analysis.a001_summary_statistics import build_cross_dataset_summary, build_dataset_summary



# ============================================================
# Tests
# ============================================================

def value_of(summary_df, metric):
    """
    Return the value for a given metric from a summary table.
    This reads a single metric cell without depending on row order.
    """

    return summary_df[summary_df["metric"] == metric]["value"].iloc[0]


def test_build_dataset_summary_counts_rows_and_employers():
    """
    Check that the dataset summary reports the row count and distinct employer count.
    This locks the compact snapshot the pipeline exports per dataset.
    """

    df = pd.DataFrame(
        {
            "company_name": ["A", "A", "B"],
            "naics2_name": ["Finance and Insurance"] * 3,
            "posted": ["2024-01-05", "2024-01-06", "2024-01-07"],
        }
    )

    summary = build_dataset_summary(df, "finance")

    assert value_of(summary, "row_count") == 3
    assert value_of(summary, "unique_employers") == 2


def test_build_cross_dataset_summary_counts_shared_employers():
    """
    Check that the cross-dataset summary counts employers shared across both datasets.
    This confirms the overlap comparison the pipeline reports.
    """

    left_df = pd.DataFrame({"company_name": ["A", "B", "C"]})
    right_df = pd.DataFrame({"company_name": ["A", "B"]})

    cross = build_cross_dataset_summary(left_df, right_df, "left", "right")

    assert value_of(cross, "shared_employers") == 2
    assert value_of(cross, "only_in_left") == 1



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
        script_name = "t006_summary_statistics",
        log_dir = settings.LOG_DIR,
    )
