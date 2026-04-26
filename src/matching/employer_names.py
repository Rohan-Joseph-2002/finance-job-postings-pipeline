"""
AUTHOR: Rohan Joseph
PURPOSE: Employer name standardization and matching helpers.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""

from __future__ import annotations



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import re

from difflib import SequenceMatcher

import pandas as pd


# --- Import project-specific utilities and pipeline code ---
from project.settings import (
    EMPLOYER_GENERIC_TRAILING_WORDS,
    EMPLOYER_NAME_REPLACEMENTS,
    EMPLOYER_NAME_SUFFIXES,
)



"""
Functions
"""

def standardize_employer_name(value: str) -> str:
    """
    Standardize an employer name so it can be compared more reliably across datasets.
    This helps normalize legal suffixes, punctuation, and whitespace before matching.
    """

    if pd.isna(value):
        return ""

    standardized_value = str(value).lower().strip()

    for source_value, target_value in EMPLOYER_NAME_REPLACEMENTS.items():
        standardized_value = standardized_value.replace(source_value, target_value)

    standardized_value = re.sub(r"[^a-z0-9 ]", " ", standardized_value)
    standardized_value = " ".join(standardized_value.split())
    standardized_value = re.sub(r"^the ", "", standardized_value)

    tokens = standardized_value.split()

    while tokens and tokens[-1] in EMPLOYER_NAME_SUFFIXES:
        tokens = tokens[:-1]

    while len(tokens) > 1 and tokens[-1] in EMPLOYER_GENERIC_TRAILING_WORDS:
        tokens = tokens[:-1]

    return " ".join(tokens).strip()



def build_employer_standardization_frame(
    df: pd.DataFrame,
    company_col: str = "company_name",
    company_id_col: str | None = "company",
) -> pd.DataFrame:
    """
    Build a unique employer-level table with standardized names and posting counts.
    This helps separate employer matching from job-level records.
    """

    required_columns = [company_col]

    if company_id_col is not None and company_id_col in df.columns:
        required_columns.append(company_id_col)

    employer_df = df[required_columns].dropna(subset = [company_col]).copy()
    employer_df[company_col] = employer_df[company_col].astype(str).str.strip()
    employer_df["company_name_standardized"] = employer_df[company_col].apply(standardize_employer_name)
    employer_df = employer_df[employer_df["company_name_standardized"] != ""].copy()

    group_columns = [company_col, "company_name_standardized"]

    if company_id_col is not None and company_id_col in employer_df.columns:
        group_columns = [company_id_col] + group_columns

    employer_df = employer_df.groupby(group_columns, dropna = False).size().reset_index(name = "job_posting_count")
    employer_df = employer_df.sort_values(
        by = ["job_posting_count", company_col],
        ascending = [False, True],
    ).reset_index(drop = True)
    return employer_df



def compute_name_similarity(source_name: str, target_name: str) -> float:
    """
    Compute a similarity score between two standardized employer names.
    This helps support a light-weight fuzzy matching fallback after exact matching.
    """

    direct_similarity = SequenceMatcher(None, source_name, target_name).ratio()
    source_tokens = " ".join(sorted(source_name.split()))
    target_tokens = " ".join(sorted(target_name.split()))
    token_similarity = SequenceMatcher(None, source_tokens, target_tokens).ratio()
    return max(direct_similarity, token_similarity)



def match_standardized_employers(
    source_employers_df: pd.DataFrame,
    reference_employers_df: pd.DataFrame,
    threshold: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Match standardized source employers to a standardized reference employer list.
    This helps produce an auditable match table plus a list of unmatched employers.
    """

    deduplicated_reference_df = (
        reference_employers_df
        .sort_values(
            by = ["percentage_relevant_jobs", "job_posting_count"],
            ascending = [False, False],
        )
        .drop_duplicates(subset = ["company_name_standardized"])
        .reset_index(drop = True)
    )

    reference_lookup = deduplicated_reference_df.set_index("company_name_standardized").to_dict("index")
    matched_rows: list[dict[str, object]] = []
    unmatched_rows: list[dict[str, object]] = []

    for _, source_row in source_employers_df.iterrows():
        standardized_name = source_row["company_name_standardized"]

        if standardized_name in reference_lookup:
            reference_row = reference_lookup[standardized_name]
            matched_rows.append({
                "source_company": source_row.get("company"),
                "source_company_name": source_row["company_name"],
                "source_company_name_standardized": standardized_name,
                "source_job_posting_count": source_row["job_posting_count"],
                "reference_company": reference_row.get("company"),
                "reference_company_name": reference_row["company_name"],
                "reference_company_name_standardized": standardized_name,
                "reference_job_posting_count": reference_row["job_posting_count"],
                "percentage_relevant_jobs": reference_row["percentage_relevant_jobs"],
                "match_method": "exact_standardized_name",
                "match_score": 1.0,
            })
            continue

        best_match: dict[str, object] | None = None
        best_score = 0.0

        for _, reference_row in deduplicated_reference_df.iterrows():
            score = compute_name_similarity(standardized_name, reference_row["company_name_standardized"])

            if score > best_score:
                best_score = score
                best_match = reference_row.to_dict()

        if best_match is not None and best_score >= threshold:
            matched_rows.append({
                "source_company": source_row.get("company"),
                "source_company_name": source_row["company_name"],
                "source_company_name_standardized": standardized_name,
                "source_job_posting_count": source_row["job_posting_count"],
                "reference_company": best_match.get("company"),
                "reference_company_name": best_match["company_name"],
                "reference_company_name_standardized": best_match["company_name_standardized"],
                "reference_job_posting_count": best_match["job_posting_count"],
                "percentage_relevant_jobs": best_match["percentage_relevant_jobs"],
                "match_method": "fuzzy_standardized_name",
                "match_score": round(best_score, 6),
            })
        else:
            unmatched_rows.append({
                "source_company": source_row.get("company"),
                "source_company_name": source_row["company_name"],
                "source_company_name_standardized": standardized_name,
                "source_job_posting_count": source_row["job_posting_count"],
            })

    matched_df = pd.DataFrame(matched_rows)
    unmatched_df = pd.DataFrame(unmatched_rows)
    return matched_df, unmatched_df
