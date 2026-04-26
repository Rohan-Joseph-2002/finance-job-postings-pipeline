"""
AUTHOR: Rohan Joseph
PURPOSE: Summary statistics helpers for job postings datasets.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import pandas as pd


# --- Import project-specific utilities and pipeline code ---
from project.settings import SUMMARY_CATEGORY_COLUMNS, SUMMARY_TOP_N



"""
Functions
"""

def build_dataset_summary(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """
    Build a compact summary statistics table for a job postings dataset.
    This helps produce a shareable analytical snapshot from pipeline outputs.
    """

    summary_rows: list[dict[str, object]] = []

    summary_rows.append({
        "section": "dataset_info",
        "metric": "row_count",
        "value": int(df.shape[0]),
        "notes": f"Total number of rows in {dataset_name}.",
    })
    summary_rows.append({
        "section": "dataset_info",
        "metric": "column_count",
        "value": int(df.shape[1]),
        "notes": f"Total number of columns in {dataset_name}.",
    })

    if "company_name" in df.columns:
        summary_rows.append({
            "section": "dataset_info",
            "metric": "unique_employers",
            "value": int(df["company_name"].dropna().nunique()),
            "notes": f"Number of distinct employer names in {dataset_name}.",
        })

    for column_name in SUMMARY_CATEGORY_COLUMNS:
        if column_name not in df.columns:
            continue

        top_values = df[column_name].dropna().astype(str).value_counts().head(SUMMARY_TOP_N)

        for value_label, count_value in top_values.items():
            summary_rows.append({
                "section": f"top_{column_name}",
                "metric": value_label,
                "value": int(count_value),
                "notes": f"Top observed value in column `{column_name}` for {dataset_name}.",
            })

    if "posted" in df.columns:
        posted_series = pd.to_datetime(df["posted"], errors = "coerce").dropna()

        if not posted_series.empty:
            summary_rows.append({
                "section": "date_range",
                "metric": "min_posted_date",
                "value": posted_series.min().date().isoformat(),
                "notes": f"Earliest posted date in {dataset_name}.",
            })
            summary_rows.append({
                "section": "date_range",
                "metric": "max_posted_date",
                "value": posted_series.max().date().isoformat(),
                "notes": f"Latest posted date in {dataset_name}.",
            })

    return pd.DataFrame(summary_rows)



def build_cross_dataset_summary(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    left_name: str,
    right_name: str,
) -> pd.DataFrame:
    """
    Compare two job postings datasets at a high level.
    This helps summarize how employer-filtered outputs differ from the broader finance sample.
    """

    summary_rows: list[dict[str, object]] = []

    summary_rows.append({
        "section": "dataset_comparison",
        "metric": f"row_count_{left_name}",
        "value": int(left_df.shape[0]),
        "notes": f"Total rows in {left_name}.",
    })
    summary_rows.append({
        "section": "dataset_comparison",
        "metric": f"row_count_{right_name}",
        "value": int(right_df.shape[0]),
        "notes": f"Total rows in {right_name}.",
    })

    if "company_name" in left_df.columns and "company_name" in right_df.columns:
        left_employers = set(left_df["company_name"].dropna().astype(str))
        right_employers = set(right_df["company_name"].dropna().astype(str))

        summary_rows.append({
            "section": "employer_comparison",
            "metric": "shared_employers",
            "value": int(len(left_employers.intersection(right_employers))),
            "notes": "Number of employer names appearing in both datasets.",
        })
        summary_rows.append({
            "section": "employer_comparison",
            "metric": f"employers_only_in_{left_name}",
            "value": int(len(left_employers - right_employers)),
            "notes": f"Employer names only appearing in {left_name}.",
        })
        summary_rows.append({
            "section": "employer_comparison",
            "metric": f"employers_only_in_{right_name}",
            "value": int(len(right_employers - left_employers)),
            "notes": f"Employer names only appearing in {right_name}.",
        })

    return pd.DataFrame(summary_rows)
