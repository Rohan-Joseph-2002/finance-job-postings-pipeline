"""
AUTHOR: Rohan Joseph
PURPOSE: Tests for summary statistics helpers.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import pandas as pd


# --- Import project-specific utilities and pipeline code ---
from analysis.summary_statistics import (
    build_cross_dataset_summary,
    build_dataset_summary,
)



"""
Tests
"""

def test_build_dataset_summary_includes_basic_dataset_info():
    """
    Test that build dataset summary includes basic dataset info.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """
    df = pd.DataFrame({
        "company_name": ["A Corp", "B Corp"],
        "naics2_name": ["Finance and Insurance", "Finance and Insurance"],
        "title_clean": ["analyst", "associate"],
        "posted": ["2021-01-01", "2021-02-01"],
    })

    summary_df = build_dataset_summary(df, "finance_related_jobs")

    assert "row_count" in set(summary_df["metric"])
    assert "unique_employers" in set(summary_df["metric"])


def test_build_cross_dataset_summary_reports_shared_employers():
    """
    Test that build cross dataset summary reports shared employers.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """
    left_df = pd.DataFrame({"company_name": ["A Corp", "B Corp"]})
    right_df = pd.DataFrame({"company_name": ["B Corp", "C Corp"]})

    summary_df = build_cross_dataset_summary(
        left_df,
        right_df,
        "finance_related_jobs",
        "employer_filtered_finance_jobs",
    )

    shared_employers_value = summary_df.loc[
        summary_df["metric"] == "shared_employers",
        "value",
    ].iloc[0]

    assert shared_employers_value == 1
