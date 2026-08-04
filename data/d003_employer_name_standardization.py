"""
AUTHOR: Rohan Joseph
PURPOSE: Standardize employer names from the combined finance-job sample and from the reference
         employer dictionary into unique employer-level tables with posting counts, writing both
         standardized tables to data-output for the matching stage.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-08-04
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import io, matching, settings, validation
from src.logger import capture_script_console_to_markdown
from src.utils import list_csv_files, print_section_header, print_stage_banner, print_status



# ============================================================
# Settings
# ============================================================

FINANCE_EMPLOYERS_PATH = os.path.join(
    settings.DATA_OUTPUT_DIR, "d003_finance_job_employers_standardized.csv"
)
REFERENCE_EMPLOYERS_PATH = os.path.join(
    settings.DATA_OUTPUT_DIR, "d003_reference_employers_standardized.csv"
)



# ============================================================
# Functions
# ============================================================

def load_finance_jobs():
    """
    Load and concatenate every Stage 2 finance-jobs export into one frame.
    This assembles the full finance sample the employer table is built from.
    """

    finance_files = list_csv_files(settings.DATA_OUTPUT_DIR, prefix = "d002_")

    if not finance_files:
        raise validation.ValidationError("Stage 2 finance-jobs outputs are required for Stage 3.")

    frames = [io.read_csv(path, keep_empty_as_str = True) for path in finance_files]

    return pd.concat(frames, ignore_index = True)


def build_reference_employers(reference_df):
    """
    Build the standardized reference employer table and re-attach its relevance columns.
    This gives the matching stage a reference list carrying its posting-relevance metadata.
    """

    reference_employers_df = matching.build_employer_standardization_frame(reference_df)
    relevance_df = reference_df[settings.REFERENCE_EMPLOYER_COLUMNS].drop_duplicates()

    return reference_employers_df.merge(
        relevance_df, on = ["company", "company_name"], how = "left"
    )



# ============================================================
# Main Execution
# ============================================================

def run():
    """
    Standardize finance-job and reference employers, then write both standardized tables.
    This is the stage entry point for both run_all.py and standalone manual runs.
    """

    print_section_header("Loading Finance Jobs and Reference")

    finance_df = load_finance_jobs()

    dictionary_path = settings.EMPLOYER_DICTIONARY_PATH
    validation.require_existing_file(dictionary_path, context = "employer dictionary")
    reference_df = io.read_csv(dictionary_path, keep_empty_as_str = True)
    validation.require_columns(
        reference_df, settings.REFERENCE_EMPLOYER_COLUMNS, context = "employer dictionary"
    )

    print_status(f"Loaded {len(finance_df)} finance rows and {len(reference_df)} reference rows.")

    print_section_header("Standardizing Employer Names")

    finance_employers_df = matching.build_employer_standardization_frame(finance_df)
    reference_employers_df = build_reference_employers(reference_df)

    io.write_csv(finance_employers_df, FINANCE_EMPLOYERS_PATH)
    io.write_csv(reference_employers_df, REFERENCE_EMPLOYERS_PATH)

    finance_count = len(finance_employers_df)
    reference_count = len(reference_employers_df)
    print_status(f"Standardized {finance_count} finance and {reference_count} reference employers.")


def main():
    """
    Run the employer name standardization stage behind a labelled banner.
    This gives the stage one predictable entry point that also reads well in the logs.
    """

    print_stage_banner("Data 003 | Employer Name Standardization")
    run()


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "d003_employer_name_standardization",
        log_dir = settings.LOG_DIR,
    )
