"""
AUTHOR: Rohan Joseph
PURPOSE: Tests for Stage 2 finance-related job filtering logic.
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
from pipelines.finance_related import filter_finance_related_jobs



"""
Tests
"""


def test_filter_finance_related_jobs_requires_two_signals():
    """
    Test that filter finance related jobs requires two signals.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """
    df = pd.DataFrame(
        [
            {
                "id": "job-1",
                "naics2_name": "Finance and Insurance",
                "cip6_name": "History",
                "skills_name": "relationship building",
                "title_clean": "operations coordinator",
            },
            {
                "id": "job-2",
                "naics2_name": "Finance and Insurance",
                "cip6_name": "Accounting",
                "skills_name": "relationship building",
                "title_clean": "operations coordinator",
            },
            {
                "id": "job-3",
                "naics2_name": "Retail Trade",
                "cip6_name": "History",
                "skills_name": "marketing",
                "title_clean": "store manager",
            },
        ]
    )

    filtered_df = filter_finance_related_jobs(df)

    assert list(filtered_df["id"]) == ["job-2"]
