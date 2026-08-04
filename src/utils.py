"""
AUTHOR: Rohan Joseph
PURPOSE: Provide console-formatting and file-discovery helpers shared by two or more stage
         scripts, keeping single-use helpers out of this module and inside the script that needs
         them.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-08-04
MODIFIED BY: Rohan Joseph
"""



# ============================================================
# Importing Libraries and Utilities
# ============================================================

import os
import glob



# ============================================================
# File Discovery
# ============================================================

def list_csv_files(directory, prefix = ""):
    """
    List visible CSV files in a directory, optionally restricted to a filename prefix, sorted.
    This lets a stage read the outputs of an earlier stage without hard-coding filenames.
    """

    pattern = os.path.join(directory, f"{prefix}*.csv")
    paths = [path for path in glob.glob(pattern) if not os.path.basename(path).startswith(".")]

    return sorted(paths)



# ============================================================
# Console Formatting
# ============================================================

def print_stage_banner(title):
    """
    Print a standardized banner marking the start of a pipeline stage.
    This keeps stage boundaries easy to spot in console output and captured logs.
    """

    rule = "-" * 76
    print(f"\n{rule}\n{title}\n{rule}\n")


def print_section_header(label):
    """
    Print a lightweight section header within a stage run.
    This separates month-level or file-level work in the console transcript.
    """

    print(f"\n{label}")


def print_status(message):
    """
    Print a consistently indented status line.
    This makes run logs easier to scan without repeating formatting boilerplate.
    """

    print(f"  > {message}")
