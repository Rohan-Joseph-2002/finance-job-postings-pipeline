"""
AUTHOR: Rohan Joseph
PURPOSE: Stage 2 pipeline for constructing finance-related job samples.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""


"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
from collections import Counter

import pandas as pd


# --- Import project-specific utilities and pipeline code ---
from project.env import RuntimeConfig
from project.io import read_csv_exports
from project.paths import ProjectPaths
from project.settings import CIP_KEEP_KEYWORDS, FINANCE_KEYWORDS, TITLE_KEEP_KEYWORDS
from project.utils import ensure_parent_dir, print_section_header, print_stage_banner, print_status
from project.validation import require_columns


"""
Functions
"""

def contains_any_keyword(value: str, keywords: set[str]) -> bool:
    """
    Check whether a lowercased text value contains any keyword from a supplied keyword set.
    This helps keep text-based inclusion rules consistent across title and skills filters.
    """

    lowered = str(value).lower()
    return any(keyword in lowered for keyword in keywords)


def filter_by_naics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep rows in the finance and insurance sector.
    Useful as the strongest single industry-based inclusion rule in the pipeline.
    This keeps the selection rules explicit and reusable instead of scattering them across the stage.
    """

    filtered_df = df[df["naics2_name"].fillna("").str.contains("Finance", case = False, na = False)].copy()
    print_status(f"NAICS filter kept {len(filtered_df):,} rows out of {len(df):,}.")
    return filtered_df


def filter_by_cip_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep rows whose CIP field references finance-related or quantitative majors.
    This helps capture finance-adjacent postings with informative education requirements.
    """

    mask = df["cip6_name"].fillna("").apply(lambda value: contains_any_keyword(value, CIP_KEEP_KEYWORDS))
    filtered_df = df[mask].copy()
    print_status(f"CIP filter kept {len(filtered_df):,} rows out of {len(df):,}.")
    return filtered_df


def filter_by_skills(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep rows whose skills field contains finance-related keywords.
    This helps identify finance postings outside purely industry-coded approaches.
    """

    mask = df["skills_name"].fillna("").apply(lambda value: contains_any_keyword(value, FINANCE_KEYWORDS))
    filtered_df = df[mask].copy()
    print_status(f"Skills filter kept {len(filtered_df):,} rows out of {len(df):,}.")
    return filtered_df


def filter_by_title(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep rows whose cleaned title contains finance-related keywords.
    This helps capture function-specific finance roles across industries.
    """

    mask = df["title_clean"].fillna("").apply(lambda value: contains_any_keyword(value, TITLE_KEEP_KEYWORDS))
    filtered_df = df[mask].copy()
    print_status(f"Title filter kept {len(filtered_df):,} rows out of {len(df):,}.")
    return filtered_df


def filter_finance_related_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construct the finance-related sample by keeping jobs that appear in at least two inclusion filters.
    This helps reduce dependence on any single noisy taxonomy field.
    """

    require_columns(
        df,
        ["id", "naics2_name", "cip6_name", "skills_name", "title_clean"],
        "finance-related filtering input",
    )

    initial_count = len(df)

    filtered_frames = [
        filter_by_naics(df),
        filter_by_cip_name(df),
        filter_by_skills(df),
        filter_by_title(df),
    ]

    combined_df = pd.concat(filtered_frames, ignore_index = True)
    id_counts = Counter(combined_df["id"])
    retained_ids = [job_id for job_id, count in id_counts.items() if count >= 2]

    finance_jobs_df = df[df["id"].isin(retained_ids)].drop_duplicates().reset_index(drop = True)

    percentage_retained = (len(finance_jobs_df) / initial_count * 100) if initial_count else 0.0
    print_status(
        f"Final finance-related sample kept {len(finance_jobs_df):,} rows "
        f"out of {initial_count:,} ({percentage_retained:.2f}%)."
    )

    return finance_jobs_df


def run_finance_related_jobs(config: RuntimeConfig, paths: ProjectPaths) -> None:
    """
    Execute Stage 2 over all Stage 1 exports.
    This helps transform the negatively filtered sample into a finance-focused analytical sample.
    """

    del config

    print_stage_banner("STAGE 2 | Finance Related Jobs")

    for file_path in read_csv_exports(paths.stage_001_dir):
        print_section_header(f"Processing Stage 1 export: {os.path.basename(file_path)}")
        df = pd.read_csv(file_path)
        filtered_df = filter_finance_related_jobs(df)

        output_name = os.path.basename(file_path).replace("initial_data_filtering", "finance_related_jobs")
        output_path = os.path.join(paths.stage_002_dir, output_name)
        ensure_parent_dir(output_path)
        filtered_df.to_csv(output_path, index = False)
        print_status(f"Exported {len(filtered_df):,} rows to {output_path}.")
