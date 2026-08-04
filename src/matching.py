"""
AUTHOR: Rohan Joseph
PURPOSE: Standardize employer names and match standardized finance-sample employers to a reference
         employer list, exact first then fuzzy, producing an auditable match table and a list of
         unmatched employers. Shared by the standardization, matching, and filtering stages.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-08-04
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import re

import pandas as pd

from difflib import SequenceMatcher

from src import settings



# ============================================================
# Standardization
# ============================================================

def standardize_employer_name(value):
    """
    Standardize an employer name by folding case, punctuation, legal suffixes, and generic words.
    This lets employer names be compared reliably across the finance sample and the reference list.
    """

    if pd.isna(value):
        return ""

    standardized_value = str(value).lower().strip()

    for source_value, target_value in settings.EMPLOYER_NAME_REPLACEMENTS.items():
        standardized_value = standardized_value.replace(source_value, target_value)

    standardized_value = re.sub(r"[^a-z0-9 ]", " ", standardized_value)
    standardized_value = " ".join(standardized_value.split())
    standardized_value = re.sub(r"^the ", "", standardized_value)

    tokens = standardized_value.split()

    while tokens and tokens[-1] in settings.EMPLOYER_NAME_SUFFIXES:
        tokens = tokens[:-1]

    while len(tokens) > 1 and tokens[-1] in settings.EMPLOYER_GENERIC_TRAILING_WORDS:
        tokens = tokens[:-1]

    return " ".join(tokens).strip()


def build_employer_standardization_frame(
    df, company_col = "company_name", company_id_col = "company"
):
    """
    Build a unique employer-level table with standardized names and posting counts.
    This separates employer matching from the job-level records that feed it.
    """

    required_columns = [company_col]

    if company_id_col is not None and company_id_col in df.columns:
        required_columns.append(company_id_col)

    employer_df = df[required_columns].dropna(subset = [company_col]).copy()
    employer_df[company_col] = employer_df[company_col].astype(str).str.strip()
    employer_df["company_name_standardized"] = (
        employer_df[company_col].apply(standardize_employer_name)
    )
    employer_df = employer_df[employer_df["company_name_standardized"] != ""].copy()

    group_columns = [company_col, "company_name_standardized"]

    if company_id_col is not None and company_id_col in employer_df.columns:
        group_columns = [company_id_col, *group_columns]

    employer_df = employer_df.groupby(group_columns, dropna = False).size()
    employer_df = employer_df.reset_index(name = "job_posting_count")
    employer_df = employer_df.sort_values(
        by = ["job_posting_count", company_col], ascending = [False, True]
    )

    return employer_df.reset_index(drop = True)



# ============================================================
# Matching
# ============================================================

def compute_name_similarity(source_name, target_name):
    """
    Compute a similarity score between two standardized employer names.
    This supports a lightweight fuzzy fallback after exact standardized-name matching.
    """

    direct_similarity = SequenceMatcher(None, source_name, target_name).ratio()
    source_tokens = " ".join(sorted(source_name.split()))
    target_tokens = " ".join(sorted(target_name.split()))
    token_similarity = SequenceMatcher(None, source_tokens, target_tokens).ratio()

    return max(direct_similarity, token_similarity)


def build_matched_row(source_row, reference_row, reference_standardized, match_method, match_score):
    """
    Build one matched employer record linking a source employer to a reference employer.
    This keeps the exact and fuzzy match branches producing an identical, auditable row shape.
    """

    return {
        "source_company": source_row.get("company"),
        "source_company_name": source_row["company_name"],
        "source_company_name_standardized": source_row["company_name_standardized"],
        "source_job_posting_count": source_row["job_posting_count"],
        "reference_company": reference_row.get("company"),
        "reference_company_name": reference_row["company_name"],
        "reference_company_name_standardized": reference_standardized,
        "reference_job_posting_count": reference_row["job_posting_count"],
        "percentage_relevant_jobs": reference_row["percentage_relevant_jobs"],
        "match_method": match_method,
        "match_score": match_score,
    }


def build_unmatched_row(source_row):
    """
    Build one unmatched employer record for a source employer with no reference match.
    This keeps the unmatched output auditable alongside the matched table.
    """

    return {
        "source_company": source_row.get("company"),
        "source_company_name": source_row["company_name"],
        "source_company_name_standardized": source_row["company_name_standardized"],
        "source_job_posting_count": source_row["job_posting_count"],
    }


def find_fuzzy_match(standardized_name, reference_df, threshold):
    """
    Find the best fuzzy reference match for a standardized name at or above the threshold.
    This is the fallback used when no exact standardized-name match exists.
    """

    best_match = None
    best_score = 0.0

    for _, reference_row in reference_df.iterrows():
        reference_name = reference_row["company_name_standardized"]
        score = compute_name_similarity(standardized_name, reference_name)

        if score > best_score:
            best_score = score
            best_match = reference_row.to_dict()

    if best_match is not None and best_score >= threshold:
        return best_match, round(best_score, 6)

    return None, round(best_score, 6)


def match_standardized_employers(source_employers_df, reference_employers_df, threshold):
    """
    Match standardized source employers to a standardized reference employer list.
    This produces an auditable match table plus a list of unmatched source employers.
    """

    deduplicated_reference_df = reference_employers_df.sort_values(
        by = ["percentage_relevant_jobs", "job_posting_count"], ascending = [False, False]
    )
    deduplicated_reference_df = deduplicated_reference_df.drop_duplicates(
        subset = ["company_name_standardized"]
    ).reset_index(drop = True)

    indexed_reference = deduplicated_reference_df.set_index("company_name_standardized")
    reference_lookup = indexed_reference.to_dict("index")
    matched_rows = []
    unmatched_rows = []

    for _, source_row in source_employers_df.iterrows():
        standardized_name = source_row["company_name_standardized"]

        if standardized_name in reference_lookup:
            reference_row = reference_lookup[standardized_name]
            matched_rows.append(
                build_matched_row(
                    source_row, reference_row, standardized_name, "exact_standardized_name", 1.0
                )
            )
            continue

        best_match, best_score = find_fuzzy_match(
            standardized_name, deduplicated_reference_df, threshold
        )

        if best_match is not None:
            reference_standardized = best_match["company_name_standardized"]
            matched_rows.append(
                build_matched_row(
                    source_row, best_match, reference_standardized,
                    "fuzzy_standardized_name", best_score,
                )
            )
        else:
            unmatched_rows.append(build_unmatched_row(source_row))

    return pd.DataFrame(matched_rows), pd.DataFrame(unmatched_rows)
