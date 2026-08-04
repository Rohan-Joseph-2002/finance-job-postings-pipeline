"""
AUTHOR: Rohan Joseph
PURPOSE: Summarize the finance-related and employer-filtered job samples — row and employer counts,
         top category values, date ranges, and a cross-dataset comparison — writing the summary
         tables to analysis-output.
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

from src import io, settings, validation
from src.logger import capture_script_console_to_markdown
from src.utils import list_csv_files, print_section_header, print_stage_banner, print_status



# ============================================================
# Settings
# ============================================================

FINANCE_SUMMARY_PATH = os.path.join(
    settings.ANALYSIS_OUTPUT_DIR, "a001_finance_related_jobs_summary.csv"
)
EMPLOYER_SUMMARY_PATH = os.path.join(
    settings.ANALYSIS_OUTPUT_DIR, "a001_employer_filtered_finance_jobs_summary.csv"
)
CROSS_SUMMARY_PATH = os.path.join(
    settings.ANALYSIS_OUTPUT_DIR, "a001_cross_dataset_summary.csv"
)



# ============================================================
# Functions
# ============================================================

def summary_row(section, metric, value, notes):
    """
    Build one summary record with a section, metric, value, and note.
    This keeps the summary builders compact and their row shape consistent.
    """

    return {"section": section, "metric": metric, "value": value, "notes": notes}


def build_top_value_rows(df, dataset_name):
    """
    Build top-value frequency rows for each configured category column present in the frame.
    This surfaces the most common employers and taxonomy labels in the dataset.
    """

    rows = []

    for column_name in settings.SUMMARY_CATEGORY_COLUMNS:
        if column_name not in df.columns:
            continue

        value_counts = df[column_name].dropna().astype(str).value_counts()
        top_values = value_counts.head(settings.SUMMARY_TOP_N)

        for value_label, count_value in top_values.items():
            note = f"Top value in {column_name} for {dataset_name}."
            rows.append(summary_row(f"top_{column_name}", value_label, int(count_value), note))

    return rows


def build_dataset_summary(df, dataset_name):
    """
    Build a compact summary-statistics table for one job-postings dataset.
    This produces a shareable analytical snapshot directly from the pipeline outputs.
    """

    rows = [
        summary_row("dataset_info", "row_count", len(df), "Total rows."),
        summary_row("dataset_info", "column_count", df.shape[1], "Total columns."),
    ]

    if "company_name" in df.columns:
        unique_employers = int(df["company_name"].dropna().nunique())
        rows.append(
            summary_row("dataset_info", "unique_employers", unique_employers, "Distinct employers.")
        )

    rows.extend(build_top_value_rows(df, dataset_name))

    if "posted" in df.columns:
        posted_series = pd.to_datetime(df["posted"], errors = "coerce").dropna()

        if not posted_series.empty:
            min_date = posted_series.min().date().isoformat()
            max_date = posted_series.max().date().isoformat()
            rows.append(
                summary_row("date_range", "min_posted_date", min_date, "Earliest posted date.")
            )
            rows.append(
                summary_row("date_range", "max_posted_date", max_date, "Latest posted date.")
            )

    return pd.DataFrame(rows)


def build_cross_dataset_summary(left_df, right_df, left_name, right_name):
    """
    Compare two job-postings datasets at a high level by rows and employer overlap.
    This summarizes how the employer-filtered output differs from the broader finance sample.
    """

    rows = [
        summary_row(
            "dataset_comparison", f"row_count_{left_name}", len(left_df), f"Rows in {left_name}."
        ),
        summary_row(
            "dataset_comparison", f"row_count_{right_name}", len(right_df), f"Rows in {right_name}."
        ),
    ]

    if "company_name" in left_df.columns and "company_name" in right_df.columns:
        left_employers = set(left_df["company_name"].dropna().astype(str))
        right_employers = set(right_df["company_name"].dropna().astype(str))
        shared = len(left_employers & right_employers)
        only_left = len(left_employers - right_employers)
        only_right = len(right_employers - left_employers)

        rows.append(
            summary_row("employer_comparison", "shared_employers", shared, "In both datasets.")
        )
        rows.append(
            summary_row("employer_comparison", f"only_in_{left_name}", only_left, "Left only.")
        )
        rows.append(
            summary_row("employer_comparison", f"only_in_{right_name}", only_right, "Right only.")
        )

    return pd.DataFrame(rows)


def load_concatenated(prefix):
    """
    Load and concatenate every data-output CSV matching a stage prefix.
    This assembles a full sample from the per-month files an earlier stage wrote.
    """

    files = list_csv_files(settings.DATA_OUTPUT_DIR, prefix = prefix)

    if not files:
        raise validation.ValidationError(f"No data-output files found for prefix {prefix}.")

    frames = [io.read_csv(path, keep_empty_as_str = True) for path in files]

    return pd.concat(frames, ignore_index = True)



# ============================================================
# Main Execution
# ============================================================

def run():
    """
    Load the finance and employer-filtered samples and write the three summary tables.
    This is the stage entry point for both run_all.py and standalone manual runs.
    """

    print_section_header("Loading Pipeline Samples")

    finance_df = load_concatenated("d002_")
    employer_filtered_df = load_concatenated("d005_")

    print_status(f"Loaded {len(finance_df)} finance and {len(employer_filtered_df)} filtered rows.")

    print_section_header("Building Summary Tables")

    finance_summary_df = build_dataset_summary(finance_df, "finance_related_jobs")
    employer_summary_df = build_dataset_summary(
        employer_filtered_df, "employer_filtered_finance_jobs"
    )
    cross_summary_df = build_cross_dataset_summary(
        finance_df, employer_filtered_df, "finance_related_jobs", "employer_filtered_finance_jobs"
    )

    io.write_csv(finance_summary_df, FINANCE_SUMMARY_PATH)
    io.write_csv(employer_summary_df, EMPLOYER_SUMMARY_PATH)
    io.write_csv(cross_summary_df, CROSS_SUMMARY_PATH)

    print_status(f"Wrote 3 summary tables ({len(finance_summary_df)} finance summary rows).")


def main():
    """
    Run the summary statistics stage behind a labelled banner.
    This gives the stage one predictable entry point that also reads well in the logs.
    """

    print_stage_banner("Analysis 001 | Summary Statistics")
    run()


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "a001_summary_statistics",
        log_dir = settings.LOG_DIR,
    )
