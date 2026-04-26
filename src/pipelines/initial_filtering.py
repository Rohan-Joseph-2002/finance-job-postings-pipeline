"""
AUTHOR: Rohan Joseph
PURPOSE: Stage 1 pipeline for initial data cleaning and negative filtering.
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
from project.io import iter_gzip_csv_files, iter_month_folders, read_lightcast_chunks
from project.paths import ProjectPaths
from project.settings import (
    KEY_CATEGORY_COLUMNS,
    LIGHTCAST_MAIN_DATA_COLUMNS,
    MISSING_SENTINELS,
    NEGATIVE_FILTERS,
    REORDER_COLUMNS,
)
from project.utils import (
    drop_rows_by_values,
    ensure_parent_dir,
    print_section_header,
    print_stage_banner,
    print_status,
    reorder_columns,
)
from project.validation import require_columns


"""
Functions
"""

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a raw Lightcast chunk by normalizing missing values and dropping rows with no usable category information.
    This helps make downstream filters deterministic and schema-stable.
    """

    require_columns(df, LIGHTCAST_MAIN_DATA_COLUMNS, "initial filtering input")

    cleaned_df = df.copy()
    cleaned_df = cleaned_df.replace(MISSING_SENTINELS, pd.NA)

    # Drop rows only when every key categorization field is missing; partial metadata is still usable downstream.
    key_cols_missing_mask = cleaned_df[KEY_CATEGORY_COLUMNS].isna().all(axis = 1)
    cleaned_df = cleaned_df.loc[~key_cols_missing_mask].copy()

    print_status(f"Cleaned chunk to {len(cleaned_df):,} rows after missing-value handling.")
    return cleaned_df


def apply_negative_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply denylist-style category filters across the configured taxonomy columns.
    This helps trim obviously irrelevant sectors, occupations, and career groupings before positive finance filtering.
    """

    filtered_df = df.copy()

    for col_name, drop_values in NEGATIVE_FILTERS.items():
        # Apply each denylist against its own taxonomy column so the filter logic stays easy to audit.
        filtered_df = drop_rows_by_values(
            df = filtered_df,
            col_name = col_name,
            drop_values = drop_values,
        )

    return filtered_df.reset_index(drop = True)


def finalize_monthly_output(df: pd.DataFrame) -> pd.DataFrame:
    """
    Finalize a monthly output DataFrame by parsing dates, sorting chronologically, and reordering columns.
    This helps produce stable exports suitable for downstream analytical steps.
    """

    finalized_df = df.copy()
    finalized_df["posted"] = pd.to_datetime(finalized_df["posted"], errors = "coerce")
    finalized_df["expired"] = pd.to_datetime(finalized_df["expired"], errors = "coerce")
    finalized_df = finalized_df.sort_values(by = "posted", kind = "stable")
    finalized_df = reorder_columns(finalized_df, REORDER_COLUMNS)
    return finalized_df.reset_index(drop = True)


def process_month_folder(
    month_label: str,
    month_dir: str,
    config: RuntimeConfig,
    paths: ProjectPaths,
) -> pd.DataFrame:
    """
    Process one month of raw Lightcast files into a single cleaned and negatively filtered monthly DataFrame.
    This helps keep the stage logic modular and month-scoped.
    """

    monthly_frames: list[pd.DataFrame] = []

    print_section_header(f"Processing month folder: {month_label}")

    for file_path in iter_gzip_csv_files(month_dir):
        print_status(f"Processing file: {os.path.basename(file_path)}")

        for chunk in read_lightcast_chunks(
            file_path = file_path,
            usecols = LIGHTCAST_MAIN_DATA_COLUMNS,
            chunk_size = config.chunk_size,
        ):
            cleaned_chunk = clean_dataframe(chunk)
            filtered_chunk = apply_negative_filters(cleaned_chunk)

            if not filtered_chunk.empty:
                # Keep chunk outputs in memory until the whole month is assembled into one stable export.
                monthly_frames.append(filtered_chunk)

    if not monthly_frames:
        return pd.DataFrame(columns = LIGHTCAST_MAIN_DATA_COLUMNS)

    monthly_df = pd.concat(monthly_frames, ignore_index = True)
    monthly_df = finalize_monthly_output(monthly_df)

    output_path = os.path.join(paths.stage_001_dir, f"{month_label}_initial_data_filtering.csv")
    ensure_parent_dir(output_path)
    monthly_df.to_csv(output_path, index = False)

    print_status(f"Exported {len(monthly_df):,} rows to {output_path}.")
    return monthly_df


def run_initial_data_filtering(config: RuntimeConfig, paths: ProjectPaths) -> None:
    """
    Execute Stage 1 over all available month folders.
    This helps construct the initial cleaned sample used by downstream finance filters.
    """

    if config.raw_lightcast_dir is None:
        raise ValueError("RAW_LIGHTCAST_DIR must be set before running Stage 1.")

    print_stage_banner("STAGE 1 | Initial Data Filtering")

    for month_label, month_dir in iter_month_folders(config.raw_lightcast_dir):
        process_month_folder(
            month_label = month_label,
            month_dir = month_dir,
            config = config,
            paths = paths,
        )
