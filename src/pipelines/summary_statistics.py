"""
AUTHOR: Rohan Joseph
PURPOSE: Stage 6 pipeline for summary statistics generation.
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
from analysis.summary_statistics import (
    build_cross_dataset_summary,
    build_dataset_summary,
)
from project.env import RuntimeConfig
from project.io import read_csv_exports
from project.paths import ProjectPaths
from project.utils import ensure_parent_dir, print_stage_banner, print_status



"""
Functions
"""

def run_summary_statistics(config: RuntimeConfig, paths: ProjectPaths) -> None:
    """
    Execute Stage 6 by generating summary tables for the main finance sample and employer-filtered sample.
    This helps produce analysis-ready outputs directly from the pipeline.
    """

    del config

    print_stage_banner("STAGE 6 | Summary Statistics")

    finance_frames = [pd.read_csv(file_path) for file_path in read_csv_exports(paths.stage_002_dir)]
    employer_filtered_frames = [pd.read_csv(file_path) for file_path in read_csv_exports(paths.stage_005_dir)]

    if not finance_frames or not employer_filtered_frames:
        raise ValueError("Stage 2 and Stage 5 outputs are required before running Stage 6.")

    finance_df = pd.concat(finance_frames, ignore_index = True)
    employer_filtered_df = pd.concat(employer_filtered_frames, ignore_index = True)

    finance_summary_df = build_dataset_summary(finance_df, "finance_related_jobs")
    employer_filtered_summary_df = build_dataset_summary(
        employer_filtered_df,
        "employer_filtered_finance_jobs",
    )
    cross_summary_df = build_cross_dataset_summary(
        finance_df,
        employer_filtered_df,
        "finance_related_jobs",
        "employer_filtered_finance_jobs",
    )

    finance_summary_path = os.path.join(paths.stage_006_dir, "finance_related_jobs_summary_statistics.csv")
    employer_summary_path = os.path.join(paths.stage_006_dir, "employer_filtered_finance_jobs_summary_statistics.csv")
    cross_summary_path = os.path.join(paths.stage_006_dir, "cross_dataset_summary_statistics.csv")

    ensure_parent_dir(finance_summary_path)
    finance_summary_df.to_csv(finance_summary_path, index = False)
    employer_filtered_summary_df.to_csv(employer_summary_path, index = False)
    cross_summary_df.to_csv(cross_summary_path, index = False)

    print_status(f"Exported finance-related jobs summary statistics to {finance_summary_path}.")
    print_status(f"Exported employer-filtered finance jobs summary statistics to {employer_summary_path}.")
    print_status(f"Exported cross-dataset summary statistics to {cross_summary_path}.")
