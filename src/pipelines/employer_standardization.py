"""
AUTHOR: Rohan Joseph
PURPOSE: Stage 3 pipeline for employer name standardization.
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
from matching.employer_names import build_employer_standardization_frame
from project.paths import ProjectPaths
from project.utils import ensure_parent_dir, print_stage_banner, print_status



"""
Functions
"""

def run_employer_name_standardization(config: RuntimeConfig, paths: ProjectPaths) -> None:
    """
    Execute Stage 3 by standardizing employer names from finance-job outputs and the reference employer file.
    This helps create auditable employer-level inputs for the matching stage.
    """

    if config.employer_job_postings_path is None:
        raise ValueError("EMPLOYER_JOB_POSTINGS_PATH must be set before running Stage 3.")

    print_stage_banner("STAGE 3 | Employer Name Standardization")

    finance_frames = [pd.read_csv(file_path) for file_path in read_csv_exports(paths.stage_002_dir)]

    if not finance_frames:
        raise ValueError("Stage 2 outputs are required before running Stage 3.")

    finance_df = pd.concat(finance_frames, ignore_index = True)
    finance_employers_df = build_employer_standardization_frame(finance_df)

    reference_df = pd.read_csv(config.employer_job_postings_path)
    reference_employers_df = build_employer_standardization_frame(reference_df)
    reference_employers_df = reference_employers_df.merge(
        reference_df[[
            "company",
            "company_name",
            "percentage_relevant_jobs",
            "count_of_relevant_jobs",
            "total_count_of_jobs",
        ]].drop_duplicates(),
        on = ["company", "company_name"],
        how = "left",
    )

    finance_output_path = os.path.join(paths.stage_003_dir, "finance_job_employers_standardized.csv")
    reference_output_path = os.path.join(paths.stage_003_dir, "reference_employers_standardized.csv")

    ensure_parent_dir(finance_output_path)
    finance_employers_df.to_csv(finance_output_path, index = False)
    reference_employers_df.to_csv(reference_output_path, index = False)

    print_status(f"Exported {len(finance_employers_df):,} standardized finance-job employers.")
    print_status(f"Exported {len(reference_employers_df):,} standardized reference employers.")
