"""
AUTHOR: Rohan Joseph
PURPOSE: Tests for Stage 1 initial cleaning and negative filtering logic.
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
from pipelines.initial_filtering import apply_negative_filters, clean_dataframe



"""
Tests
"""


def test_clean_dataframe_drops_rows_with_all_key_categories_missing():
    """
    Test that clean dataframe drops rows with all key categories missing.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """
    df = pd.DataFrame(
        [
            {
                "id": "1",
                "company": "A",
                "company_name": "A Corp",
                "posted": "2021-01-01",
                "expired": "2021-02-01",
                "cip6_name": "Finance, General",
                "naics2_name": None,
                "soc_2_name": None,
                "lot_career_area_name": None,
                "onet_name": None,
                "lot_occupation_group_name": None,
                "lot_specialized_occupation_name": None,
                "title_clean": "analyst",
                "skills_name": "finance",
            },
            {
                "id": "2",
                "company": "B",
                "company_name": "B Corp",
                "posted": "2021-01-01",
                "expired": "2021-02-01",
                "cip6_name": "Accounting",
                "naics2_name": "Finance and Insurance",
                "soc_2_name": "Business and Financial Operations Occupations",
                "lot_career_area_name": "Business and Finance",
                "onet_name": "Financial and Investment Analysts",
                "lot_occupation_group_name": "Finance Group",
                "lot_specialized_occupation_name": "Finance Specialist",
                "title_clean": "financial analyst",
                "skills_name": "financial analysis",
            },
        ]
    )

    cleaned_df = clean_dataframe(df)

    assert list(cleaned_df["id"]) == ["2"]


def test_apply_negative_filters_removes_denied_sector_rows():
    """
    Test that apply negative filters removes denied sector rows.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """
    df = pd.DataFrame(
        [
            {
                "id": "1",
                "company": "A",
                "company_name": "A Corp",
                "posted": "2021-01-01",
                "expired": "2021-02-01",
                "cip6_name": "Finance, General",
                "naics2_name": "Retail Trade",
                "soc_2_name": "Business and Financial Operations Occupations",
                "lot_career_area_name": "Business and Finance",
                "onet_name": "Financial and Investment Analysts",
                "lot_occupation_group_name": "Finance Group",
                "lot_specialized_occupation_name": "Finance Specialist",
                "title_clean": "financial analyst",
                "skills_name": "financial analysis",
            },
            {
                "id": "2",
                "company": "B",
                "company_name": "B Corp",
                "posted": "2021-01-01",
                "expired": "2021-02-01",
                "cip6_name": "Finance, General",
                "naics2_name": "Finance and Insurance",
                "soc_2_name": "Business and Financial Operations Occupations",
                "lot_career_area_name": "Business and Finance",
                "onet_name": "Financial and Investment Analysts",
                "lot_occupation_group_name": "Finance Group",
                "lot_specialized_occupation_name": "Finance Specialist",
                "title_clean": "financial analyst",
                "skills_name": "financial analysis",
            },
        ]
    )

    filtered_df = apply_negative_filters(df)

    assert list(filtered_df["id"]) == ["2"]
