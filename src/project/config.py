"""
AUTHOR: Rohan Joseph
PURPOSE: Central repository configuration and stage registry.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import os



"""
Settings
"""

APP_NAME = "finance_job_postings_pipeline"

DEFAULT_STAGE_ORDER = [
    "001_initial_data_filtering",
    "002_finance_related_jobs",
    "003_employer_name_standardization",
    "004_employer_name_matching",
    "005_employer_filtered_finance_jobs",
    "006_summary_statistics",
]



"""
Functions
"""

def build_stage_script_map(project_root: str) -> dict[str, str]:
    """
    Build the canonical stage-to-script mapping for the repository.
    This helps keep orchestration logic centralized and avoid duplicated script references.
    """

    scripts_dir = os.path.join(project_root, "scripts")

    return {
        "001_initial_data_filtering": os.path.join(scripts_dir, "001_initial_data_filtering.py"),
        "002_finance_related_jobs": os.path.join(scripts_dir, "002_finance_related_jobs.py"),
        "003_employer_name_standardization": os.path.join(scripts_dir, "003_employer_name_standardization.py"),
        "004_employer_name_matching": os.path.join(scripts_dir, "004_employer_name_matching.py"),
        "005_employer_filtered_finance_jobs": os.path.join(scripts_dir, "005_employer_filtered_finance_jobs.py"),
        "006_summary_statistics": os.path.join(scripts_dir, "006_summary_statistics.py"),
    }
