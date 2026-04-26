"""
AUTHOR: Rohan Joseph
PURPOSE: Tests for employer name standardization and matching logic.
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
from matching.employer_names import (
    build_employer_standardization_frame,
    match_standardized_employers,
    standardize_employer_name,
)



"""
Tests
"""

def test_standardize_employer_name_removes_common_suffixes():
    """
    Test that standardize employer name removes common suffixes.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """
    standardized_name = standardize_employer_name("The North Shore Capital LLC")

    assert standardized_name == "north shore capital"


def test_match_standardized_employers_matches_exact_standardized_names():
    """
    Test that match standardized employers matches exact standardized names.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """
    source_df = pd.DataFrame({
        "company": [1001],
        "company_name": ["North Shore Capital LLC"],
        "job_posting_count": [3],
        "company_name_standardized": ["north shore capital"],
    })
    reference_df = pd.DataFrame({
        "company": [2001],
        "company_name": ["North Shore Capital"],
        "job_posting_count": [10],
        "company_name_standardized": ["north shore capital"],
        "percentage_relevant_jobs": [0.95],
    })

    matched_df, unmatched_df = match_standardized_employers(
        source_employers_df = source_df,
        reference_employers_df = reference_df,
        threshold = 0.92,
    )

    assert list(matched_df["match_method"]) == ["exact_standardized_name"]
    assert unmatched_df.empty


def test_build_employer_standardization_frame_counts_duplicate_postings():
    """
    Test that build employer standardization frame counts duplicate postings.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """
    employer_df = pd.DataFrame({
        "company": [1, 1, 2],
        "company_name": ["North Shore Capital LLC", "North Shore Capital LLC", "Union Crest Bank Inc"],
    })

    standardized_df = build_employer_standardization_frame(employer_df)

    assert list(standardized_df["job_posting_count"]) == [2, 1]
