"""
AUTHOR: Rohan Joseph
PURPOSE: Stage 4 pipeline for employer name matching.
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
from matching.employer_names import match_standardized_employers
from project.paths import ProjectPaths
from project.utils import ensure_parent_dir, print_stage_banner, print_status



"""
Functions
"""

def run_employer_name_matching(config: RuntimeConfig, paths: ProjectPaths) -> None:
    """
    Execute Stage 4 by matching standardized finance-job employers to the reference employer list.
    This helps create a reusable employer match table for downstream filtering and analysis.
    """

    print_stage_banner("STAGE 4 | Employer Name Matching")

    finance_employers_path = os.path.join(paths.stage_003_dir, "finance_job_employers_standardized.csv")
    reference_employers_path = os.path.join(paths.stage_003_dir, "reference_employers_standardized.csv")

    if not os.path.exists(finance_employers_path) or not os.path.exists(reference_employers_path):
        raise ValueError("Stage 3 standardized employer outputs are required before running Stage 4.")

    finance_employers_df = pd.read_csv(finance_employers_path)
    reference_employers_df = pd.read_csv(reference_employers_path)

    matched_df, unmatched_df = match_standardized_employers(
        source_employers_df = finance_employers_df,
        reference_employers_df = reference_employers_df,
        threshold = config.employer_match_threshold,
    )

    matched_output_path = os.path.join(paths.stage_004_dir, "employer_name_matches.csv")
    unmatched_output_path = os.path.join(paths.stage_004_dir, "unmatched_finance_job_employers.csv")

    ensure_parent_dir(matched_output_path)
    matched_df.to_csv(matched_output_path, index = False)
    unmatched_df.to_csv(unmatched_output_path, index = False)

    print_status(f"Exported {len(matched_df):,} employer matches.")
    print_status(f"Exported {len(unmatched_df):,} unmatched finance-job employers.")
