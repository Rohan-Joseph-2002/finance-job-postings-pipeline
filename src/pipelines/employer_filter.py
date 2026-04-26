"""
AUTHOR: Rohan Joseph
PURPOSE: Stage 5 pipeline for employer-filtered finance job sample construction.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
import pandas as pd


# --- Import project-specific utilities and pipeline code ---
from project.env import RuntimeConfig
from project.io import read_csv_exports
from matching.employer_names import standardize_employer_name
from project.paths import ProjectPaths
from project.utils import ensure_parent_dir, print_section_header, print_stage_banner, print_status



"""
Functions
"""

def run_employer_filtered_finance_jobs(config: RuntimeConfig, paths: ProjectPaths) -> None:
    """
    Execute Stage 5 by filtering finance-job outputs to employers that matched the reference list.
    This helps produce a stricter finance-job sample linked to the employer relevance dictionary.
    """

    del config

    print_stage_banner("STAGE 5 | Employer Filtered Finance Jobs")

    matches_path = os.path.join(paths.stage_004_dir, "employer_name_matches.csv")

    if not os.path.exists(matches_path):
        raise ValueError("Stage 4 employer matches are required before running Stage 5.")

    matched_employers_df = pd.read_csv(matches_path)
    matched_columns = [
        "source_company_name_standardized",
        "reference_company",
        "reference_company_name",
        "reference_company_name_standardized",
        "reference_job_posting_count",
        "percentage_relevant_jobs",
        "match_method",
        "match_score",
    ]
    matched_employers_df = matched_employers_df[matched_columns].drop_duplicates(
        subset = ["source_company_name_standardized"]
    )

    for file_path in read_csv_exports(paths.stage_002_dir):
        print_section_header(f"Processing Stage 2 export: {os.path.basename(file_path)}")
        finance_jobs_df = pd.read_csv(file_path)
        finance_jobs_df["source_company_name_standardized"] = (
            finance_jobs_df["company_name"].fillna("").astype(str).apply(standardize_employer_name)
        )

        filtered_df = finance_jobs_df.merge(
            matched_employers_df,
            on = "source_company_name_standardized",
            how = "inner",
        )

        output_name = os.path.basename(file_path).replace("finance_related_jobs", "employer_filtered_finance_jobs")
        output_path = os.path.join(paths.stage_005_dir, output_name)
        ensure_parent_dir(output_path)
        filtered_df.to_csv(output_path, index = False)
        print_status(f"Exported {len(filtered_df):,} rows to {output_path}.")
