"""
AUTHOR: Rohan Joseph
PURPOSE: Test the Stage 1 cleaning and negative filtering — dropping rows with no usable category,
         normalizing missing sentinels, applying taxonomy denylists, and reordering columns.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-08-04
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import sys
import subprocess

import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import settings
from src.logger import capture_script_console_to_markdown
from data.d001_initial_data_filtering import (
    apply_negative_filters,
    clean_dataframe,
    reorder_columns,
)



# ============================================================
# Tests
# ============================================================

def postings_frame(rows):
    """
    Build a postings frame from partial rows, filling every main data column that is missing.
    This keeps the Stage 1 fixtures readable while satisfying the required-column check.
    """

    frame = pd.DataFrame(rows)

    for column in settings.LIGHTCAST_MAIN_DATA_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA

    return frame[settings.LIGHTCAST_MAIN_DATA_COLUMNS]


def test_clean_dataframe_drops_rows_with_no_category():
    """
    Check that rows with every key category missing are dropped and sentinels become NA.
    This confirms only rows with usable classification metadata survive Stage 1.
    """

    raw_df = postings_frame(
        [
            {"id": "1", "naics2_name": "Finance and Insurance"},
            {"id": "2"},
            {"id": "3", "soc_2_name": "None"},
        ]
    )

    cleaned_df = clean_dataframe(raw_df)

    assert cleaned_df["id"].tolist() == ["1"]


def test_apply_negative_filters_drops_denylisted_sectors():
    """
    Check that a denylisted industry is removed while a finance industry is kept.
    This confirms the negative filters trim clearly irrelevant sectors.
    """

    df = postings_frame(
        [
            {"id": "1", "naics2_name": "Finance and Insurance"},
            {"id": "2", "naics2_name": "Manufacturing"},
        ]
    )

    filtered_df = apply_negative_filters(df)

    assert filtered_df["id"].tolist() == ["1"]


def test_reorder_columns_moves_priority_columns_first():
    """
    Check that priority columns are moved to the front while the rest are preserved.
    This confirms exports keep a stable, predictable column order.
    """

    df = pd.DataFrame({"skills_name": ["x"], "id": ["1"], "title_clean": ["t"]})

    reordered = reorder_columns(df, ["id", "title_clean"])

    assert list(reordered.columns) == ["id", "title_clean", "skills_name"]



# ============================================================
# Main Execution
# ============================================================

def main():
    """
    Run this test module through pytest in a subprocess and echo its output.
    This logs the test run like a pipeline script without the tee fighting pytest's capture.
    """

    command = [sys.executable, "-m", "pytest", __file__, "-v"]
    result = subprocess.run(command, capture_output = True, text = True)

    print(result.stdout, end = "")
    print(result.stderr, end = "")


if __name__ == "__main__":
    capture_script_console_to_markdown(
        run_callable = main,
        script_name = "t001_initial_data_filtering",
        log_dir = settings.LOG_DIR,
    )
