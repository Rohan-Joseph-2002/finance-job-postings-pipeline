"""
AUTHOR: Rohan Joseph
PURPOSE: Shared utility functions for filtering, formatting, and diagnostics.
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



"""
Functions
"""

def print_section_header(label: str) -> None:
    """
    Print a lightweight section header within a stage run.
    This helps separate month-level or file-level work in the console transcript.
    """

    print(f"\n{label}")



def print_status(message: str) -> None:
    """
    Print a consistently indented status line.
    This helps make logs easier to scan without repeating formatting boilerplate.
    """

    print(f"  > {message}")



def drop_rows_by_values(df: pd.DataFrame, col_name: str, drop_values: list[str]) -> pd.DataFrame:
    """
    Remove rows whose values in a target column fall inside a supplied denylist.
    This helps keep the negative filtering logic consistent across stage scripts.
    """

    if col_name not in df.columns or not drop_values:
        return df

    filtered_df = df[~df[col_name].isin(drop_values)].copy()
    print_status(f"Column '{col_name}' reduced rows from {len(df):,} to {len(filtered_df):,}.")
    return filtered_df


def reorder_columns(df: pd.DataFrame, first_columns: list[str]) -> pd.DataFrame:
    """
    Reorder a DataFrame so priority columns appear first while preserving all remaining columns.
    This helps produce stable CSV exports across stages.
    """

    existing_first_columns = [col for col in first_columns if col in df.columns]
    remaining_columns = [col for col in df.columns if col not in existing_first_columns]
    return df[existing_first_columns + remaining_columns]


def ensure_parent_dir(file_path: str) -> None:
    """
    Ensure that a file's parent directory exists before writing.
    This helps avoid repeated parent-directory creation code in export steps.
    """

    os.makedirs(os.path.dirname(file_path), exist_ok = True)


def print_stage_banner(label: str) -> None:
    """
    Print a standardized banner for a pipeline stage.
    This helps make run logs easier to scan.
    """

    print("\n" + "-" * 76)
    print(label)
    print("-" * 76 + "\n")
