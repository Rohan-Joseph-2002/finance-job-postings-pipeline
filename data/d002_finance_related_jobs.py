"""
AUTHOR: Rohan Joseph
PURPOSE: Read each Stage 1 monthly export and keep the finance-related jobs — those appearing in
         at least two of four inclusion signals (industry, education field, skills, title) — so no
         single noisy taxonomy field decides inclusion, writing one file per month to data-output.
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

from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import io, settings, validation
from src.logger import capture_script_console_to_markdown
from src.utils import list_csv_files, print_section_header, print_stage_banner, print_status



# ============================================================
# Settings
# ============================================================

FINANCE_FILTER_COLUMNS = ["id", "naics2_name", "cip6_name", "skills_name", "title_clean"]



# ============================================================
# Functions
# ============================================================

def contains_any_keyword(value, keywords):
    """
    Check whether a lowercased text value contains any keyword from a supplied set.
    This keeps the text-based inclusion rules consistent across the CIP, skills, and title filters.
    """

    lowered = str(value).lower()

    return any(keyword in lowered for keyword in keywords)


def filter_by_naics(df):
    """
    Keep rows in the finance and insurance sector.
    This is the strongest single industry-based inclusion signal.
    """

    mask = df["naics2_name"].fillna("").str.contains("Finance", case = False, na = False)

    return df[mask].copy()


def filter_by_keyword_column(df, column_name, keywords):
    """
    Keep rows whose column text contains any of the supplied keywords.
    This shares one text-inclusion rule across the CIP, skills, and title signals.
    """

    mask = df[column_name].fillna("").apply(lambda value: contains_any_keyword(value, keywords))

    return df[mask].copy()


def filter_finance_related_jobs(df):
    """
    Keep jobs that appear in at least two of the four finance inclusion signals.
    This reduces dependence on any single noisy taxonomy field for finance selection.
    """

    validation.require_columns(df, FINANCE_FILTER_COLUMNS, context = "finance filtering")

    filtered_frames = [
        filter_by_naics(df),
        filter_by_keyword_column(df, "cip6_name", settings.CIP_KEEP_KEYWORDS),
        filter_by_keyword_column(df, "skills_name", settings.FINANCE_KEYWORDS),
        filter_by_keyword_column(df, "title_clean", settings.TITLE_KEEP_KEYWORDS),
    ]

    combined_df = pd.concat(filtered_frames, ignore_index = True)
    id_counts = Counter(combined_df["id"])
    retained_ids = [job_id for job_id, count in id_counts.items() if count >= 2]

    finance_jobs_df = df[df["id"].isin(retained_ids)].drop_duplicates().reset_index(drop = True)

    return finance_jobs_df



# ============================================================
# Main Execution
# ============================================================

def run():
    """
    Read each Stage 1 monthly export and write its finance-related subset to data-output.
    This is the stage entry point for both run_all.py and standalone manual runs.
    """

    print_section_header("Loading Stage 1 Exports")

    stage_one_files = list_csv_files(settings.DATA_OUTPUT_DIR, prefix = "d001_")
    print_status(f"Found {len(stage_one_files)} Stage 1 monthly exports.")

    for file_path in stage_one_files:
        print_section_header(f"Processing {os.path.basename(file_path)}")

        df = io.read_csv(file_path, keep_empty_as_str = True)
        finance_df = filter_finance_related_jobs(df)

        output_name = os.path.basename(file_path)
        output_name = output_name.replace("d001_", "d002_")
        output_name = output_name.replace("initial_data_filtering", "finance_related_jobs")
        output_path = os.path.join(settings.DATA_OUTPUT_DIR, output_name)
        io.write_csv(finance_df, output_path)

        print_status(f"Kept {len(finance_df)} finance-related rows of {len(df)}.")


def main():
    """
    Run the finance-related jobs stage behind a labelled banner.
    This gives the stage one predictable entry point that also reads well in the logs.
    """

    print_stage_banner("Data 002 | Finance Related Jobs")
    run()


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "d002_finance_related_jobs",
        log_dir = settings.LOG_DIR,
    )
