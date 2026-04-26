"""
AUTHOR: Rohan Joseph
PURPOSE: Project path definitions and directory bootstrapping helpers.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os
from dataclasses import dataclass



"""
Settings
"""

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUT_DIR = os.path.join(PROJECT_ROOT, "input")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
EXPORTS_DIR = os.path.join(OUTPUT_DIR, "exports")
LOG_DIR = os.path.join(OUTPUT_DIR, "logs")
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
TABLES_DIR = os.path.join(OUTPUT_DIR, "tables")



"""
Classes
"""

@dataclass(frozen = True)
class ProjectPaths:
    """
    Container for stage-level filesystem locations.
    This keeps path resolution in one place so scripts and stages use the same file locations.
    """

    stage_001_dir: str
    stage_002_dir: str
    stage_003_dir: str
    stage_004_dir: str
    stage_005_dir: str
    stage_006_dir: str
    log_dir: str



"""
Functions
"""

def ensure_project_directories() -> ProjectPaths:
    """
    Create the standard project directories if they do not already exist.
    This helps guarantee that scripts can write outputs and logs without repeated path boilerplate.
    """

    for directory in [
        INPUT_DIR,
        OUTPUT_DIR,
        EXPORTS_DIR,
        LOG_DIR,
        FIGURES_DIR,
        TABLES_DIR,
    ]:
        os.makedirs(directory, exist_ok = True)

    stage_001_dir = os.path.join(EXPORTS_DIR, "001_initial_data_filtering")
    stage_002_dir = os.path.join(EXPORTS_DIR, "002_finance_related_jobs")
    stage_003_dir = os.path.join(EXPORTS_DIR, "003_employer_name_standardization")
    stage_004_dir = os.path.join(EXPORTS_DIR, "004_employer_name_matching")
    stage_005_dir = os.path.join(EXPORTS_DIR, "005_employer_filtered_finance_jobs")
    stage_006_dir = os.path.join(EXPORTS_DIR, "006_summary_statistics")

    for directory in [
        stage_001_dir,
        stage_002_dir,
        stage_003_dir,
        stage_004_dir,
        stage_005_dir,
        stage_006_dir,
    ]:
        os.makedirs(directory, exist_ok = True)

    return ProjectPaths(
        stage_001_dir = stage_001_dir,
        stage_002_dir = stage_002_dir,
        stage_003_dir = stage_003_dir,
        stage_004_dir = stage_004_dir,
        stage_005_dir = stage_005_dir,
        stage_006_dir = stage_006_dir,
        log_dir = LOG_DIR,
    )
