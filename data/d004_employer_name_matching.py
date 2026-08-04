"""
AUTHOR: Rohan Joseph
PURPOSE: Match the standardized finance-job employers to the standardized reference employer list,
         exact first then fuzzy, writing the employer match table and the unmatched finance
         employers to data-output.
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
from src.utils import print_section_header, print_stage_banner, print_status



# ============================================================
# Settings
# ============================================================

FINANCE_EMPLOYERS_PATH = os.path.join(
    settings.DATA_OUTPUT_DIR, "d003_finance_job_employers_standardized.csv"
)
REFERENCE_EMPLOYERS_PATH = os.path.join(
    settings.DATA_OUTPUT_DIR, "d003_reference_employers_standardized.csv"
)
MATCHES_PATH = os.path.join(settings.DATA_OUTPUT_DIR, "d004_employer_name_matches.csv")
UNMATCHED_PATH = os.path.join(
    settings.DATA_OUTPUT_DIR, "d004_unmatched_finance_job_employers.csv"
)



# ============================================================
# Main Execution
# ============================================================

def run():
    """
    Load the standardized employer tables, match them, and write matches and unmatched employers.
    This is the stage entry point for both run_all.py and standalone manual runs.
    """

    print_section_header("Loading Standardized Employers")

    validation.require_existing_file(FINANCE_EMPLOYERS_PATH, context = "finance employers")
    validation.require_existing_file(REFERENCE_EMPLOYERS_PATH, context = "reference employers")

    finance_employers_df = io.read_csv(FINANCE_EMPLOYERS_PATH, keep_empty_as_str = True)
    reference_employers_df = io.read_csv(REFERENCE_EMPLOYERS_PATH, keep_empty_as_str = True)

    finance_count = len(finance_employers_df)
    reference_count = len(reference_employers_df)
    print_status(f"Loaded {finance_count} finance and {reference_count} reference employers.")

    print_section_header("Matching Employers")

    matched_df, unmatched_df = matching.match_standardized_employers(
        source_employers_df = finance_employers_df,
        reference_employers_df = reference_employers_df,
        threshold = settings.EMPLOYER_MATCH_THRESHOLD,
    )

    io.write_csv(matched_df, MATCHES_PATH)
    io.write_csv(unmatched_df, UNMATCHED_PATH)

    print_status(f"Matched {len(matched_df)} employers; {len(unmatched_df)} unmatched.")


def main():
    """
    Run the employer name matching stage behind a labelled banner.
    This gives the stage one predictable entry point that also reads well in the logs.
    """

    print_stage_banner("Data 004 | Employer Name Matching")
    run()


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "d004_employer_name_matching",
        log_dir = settings.LOG_DIR,
    )
