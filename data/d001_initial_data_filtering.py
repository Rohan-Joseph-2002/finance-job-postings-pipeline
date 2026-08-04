"""
AUTHOR: Rohan Joseph
PURPOSE: Read each raw monthly Lightcast posting file in chunks, normalize missing values, drop
         rows with no usable classification, and remove clearly irrelevant sectors and
         occupations, writing one cleaned, negatively filtered file per month to data-output.
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
# Functions
# ============================================================

def read_month_chunks(file_path):
    """
    Read one raw Lightcast month file in fixed-size chunks over the main data columns.
    This keeps memory bounded on large monthly exports while staying pure pandas.
    """

    compression = "gzip" if file_path.endswith(".gz") else None

    return pd.read_csv(
        file_path,
        compression = compression,
        usecols = settings.LIGHTCAST_MAIN_DATA_COLUMNS,
        dtype = "string",
        chunksize = settings.CHUNK_SIZE,
    )


def clean_dataframe(df):
    """
    Normalize missing sentinels and drop rows where every key category field is missing.
    This makes downstream filters deterministic and keeps only rows with usable metadata.
    """

    validation.require_columns(df, settings.LIGHTCAST_MAIN_DATA_COLUMNS, context = "raw postings")

    cleaned_df = df.copy()
    cleaned_df = cleaned_df.replace(settings.MISSING_SENTINELS, pd.NA)

    # Drop a row only when all key category fields are missing; partial metadata is still usable.
    missing_mask = cleaned_df[settings.KEY_CATEGORY_COLUMNS].isna().all(axis = 1)
    cleaned_df = cleaned_df.loc[~missing_mask].copy()

    return cleaned_df


def drop_rows_by_values(df, column_name, drop_values):
    """
    Remove rows whose value in a target column falls inside a supplied denylist.
    This keeps the negative-filtering logic consistent across the taxonomy columns.
    """

    if column_name not in df.columns or not drop_values:
        return df

    return df[~df[column_name].isin(drop_values)].copy()


def apply_negative_filters(df):
    """
    Apply each taxonomy denylist against its own column to trim irrelevant postings.
    This removes obviously non-finance sectors and occupations before positive filtering.
    """

    filtered_df = df.copy()

    for column_name, drop_values in settings.NEGATIVE_FILTERS.items():
        filtered_df = drop_rows_by_values(filtered_df, column_name, drop_values)

    return filtered_df.reset_index(drop = True)


def reorder_columns(df, first_columns):
    """
    Reorder a DataFrame so priority columns appear first while preserving the rest.
    This produces stable CSV exports across stages.
    """

    existing_first = [column for column in first_columns if column in df.columns]
    remaining = [column for column in df.columns if column not in existing_first]

    return df[existing_first + remaining]


def finalize_monthly_output(df):
    """
    Parse posting dates, sort chronologically, and reorder the columns of a monthly frame.
    This produces a stable export suitable for the downstream finance filter.
    """

    finalized_df = df.copy()
    finalized_df["posted"] = pd.to_datetime(finalized_df["posted"], errors = "coerce")
    finalized_df["expired"] = pd.to_datetime(finalized_df["expired"], errors = "coerce")
    finalized_df = finalized_df.sort_values(by = "posted", kind = "stable")
    finalized_df = reorder_columns(finalized_df, settings.REORDER_COLUMNS)

    return finalized_df.reset_index(drop = True)


def month_label_for(file_path):
    """
    Derive a compact month label from a raw posting filename.
    This names each month's outputs consistently through the rest of the pipeline.
    """

    stem = os.path.splitext(os.path.basename(file_path))[0]

    return stem.replace("_postings_sample", "")


def process_month_file(file_path):
    """
    Clean and negatively filter one month file across its chunks into a single frame.
    This keeps the stage logic modular and scoped to one month at a time.
    """

    monthly_frames = []

    for chunk in read_month_chunks(file_path):
        cleaned_chunk = clean_dataframe(chunk)
        filtered_chunk = apply_negative_filters(cleaned_chunk)

        if not filtered_chunk.empty:
            monthly_frames.append(filtered_chunk)

    if not monthly_frames:
        return pd.DataFrame(columns = settings.LIGHTCAST_MAIN_DATA_COLUMNS)

    monthly_df = pd.concat(monthly_frames, ignore_index = True)

    return finalize_monthly_output(monthly_df)



# ============================================================
# Main Execution
# ============================================================

def run():
    """
    Process every raw monthly Lightcast file into a cleaned, negatively filtered monthly export.
    This is the stage entry point for both run_all.py and standalone manual runs.
    """

    print_section_header("Loading Raw Lightcast Sample")

    validation.require_existing_directory(settings.RAW_LIGHTCAST_DIR, context = "Lightcast folder")
    month_files = list_csv_files(settings.RAW_LIGHTCAST_DIR)

    print_status(f"Found {len(month_files)} raw monthly files.")

    for file_path in month_files:
        month_label = month_label_for(file_path)
        print_section_header(f"Processing month: {month_label}")

        monthly_df = process_month_file(file_path)
        output_path = os.path.join(
            settings.DATA_OUTPUT_DIR, f"d001_{month_label}_initial_data_filtering.csv"
        )
        io.write_csv(monthly_df, output_path)

        print_status(f"Exported {len(monthly_df)} filtered rows for {month_label}.")


def main():
    """
    Run the initial data filtering stage behind a labelled banner.
    This gives the stage one predictable entry point that also reads well in the logs.
    """

    print_stage_banner("Data 001 | Initial Data Filtering")
    run()


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "d001_initial_data_filtering",
        log_dir = settings.LOG_DIR,
    )
