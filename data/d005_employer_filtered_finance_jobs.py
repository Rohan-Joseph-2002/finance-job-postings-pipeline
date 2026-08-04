"""
AUTHOR: Rohan Joseph
PURPOSE: Filter each month's finance-jobs sample down to postings whose employer matched the
         reference dictionary, attaching the matched employer's relevance fields, and write one
         employer-filtered file per month to data-output.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-08-04
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import io, matching, settings, validation
from src.logger import capture_script_console_to_markdown
from src.utils import list_csv_files, print_section_header, print_stage_banner, print_status



# ============================================================
# Settings
# ============================================================

MATCHES_PATH = os.path.join(settings.DATA_OUTPUT_DIR, "d004_employer_name_matches.csv")

MATCHED_EMPLOYER_COLUMNS = [
    "source_company_name_standardized",
    "reference_company",
    "reference_company_name",
    "reference_company_name_standardized",
    "reference_job_posting_count",
    "percentage_relevant_jobs",
    "match_method",
    "match_score",
]



# ============================================================
# Functions
# ============================================================

def load_matched_employers():
    """
    Load the unique matched employers keyed by their standardized source name.
    This gives the filter a one-row-per-employer lookup to join finance jobs against.
    """

    validation.require_existing_file(MATCHES_PATH, context = "employer matches")
    matched_df = io.read_csv(MATCHES_PATH, keep_empty_as_str = True)
    matched_df = matched_df[MATCHED_EMPLOYER_COLUMNS]

    return matched_df.drop_duplicates(subset = ["source_company_name_standardized"])


def filter_jobs_to_matched_employers(finance_jobs_df, matched_employers_df):
    """
    Keep only finance jobs whose standardized employer matched the reference list.
    This restricts the sample to postings linked to the employer relevance dictionary.
    """

    standardized = finance_jobs_df["company_name"].fillna("").astype(str)
    finance_jobs_df["source_company_name_standardized"] = standardized.apply(
        matching.standardize_employer_name
    )

    return finance_jobs_df.merge(
        matched_employers_df, on = "source_company_name_standardized", how = "inner"
    )



# ============================================================
# Main Execution
# ============================================================

def run():
    """
    Filter each month's finance jobs to matched employers and write the results per month.
    This is the stage entry point for both run_all.py and standalone manual runs.
    """

    print_section_header("Loading Matched Employers")

    matched_employers_df = load_matched_employers()
    finance_files = list_csv_files(settings.DATA_OUTPUT_DIR, prefix = "d002_")

    employer_count = len(matched_employers_df)
    print_status(f"Loaded {employer_count} matched employers across {len(finance_files)} months.")

    for file_path in finance_files:
        print_section_header(f"Processing {os.path.basename(file_path)}")

        finance_jobs_df = io.read_csv(file_path, keep_empty_as_str = True)
        filtered_df = filter_jobs_to_matched_employers(finance_jobs_df, matched_employers_df)

        output_name = os.path.basename(file_path).replace("d002_", "d005_")
        output_name = output_name.replace("finance_related_jobs", "employer_filtered_finance_jobs")
        output_path = os.path.join(settings.DATA_OUTPUT_DIR, output_name)
        io.write_csv(filtered_df, output_path)

        print_status(f"Kept {len(filtered_df)} employer-filtered rows of {len(finance_jobs_df)}.")


def main():
    """
    Run the employer-filtered finance jobs stage behind a labelled banner.
    This gives the stage one predictable entry point that also reads well in the logs.
    """

    print_stage_banner("Data 005 | Employer Filtered Finance Jobs")
    run()


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "d005_employer_filtered_finance_jobs",
        log_dir = settings.LOG_DIR,
    )
