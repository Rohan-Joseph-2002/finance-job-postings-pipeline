"""
AUTHOR: Rohan Joseph
PURPOSE: Input and output helpers for stage scripts.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import glob
import os
from collections.abc import Iterator

import pandas as pd



"""
Functions
"""

def is_visible_path(path: str) -> bool:
    """
    Check whether a filesystem path is a real project file or directory rather than a hidden sidecar artifact.
    This helps skip macOS metadata files such as ._* during pipeline discovery.
    """

    return not os.path.basename(path).startswith(".")



def iter_month_folders(raw_lightcast_dir: str) -> Iterator[tuple[str, str]]:
    """
    Yield month-labeled folders under the raw Lightcast directory.
    This helps standardize traversal over the nested year/month raw export structure.
    """

    year_dirs = sorted(
        [
            os.path.join(raw_lightcast_dir, path_name)
            for path_name in os.listdir(raw_lightcast_dir)
            if os.path.isdir(os.path.join(raw_lightcast_dir, path_name))
            and is_visible_path(os.path.join(raw_lightcast_dir, path_name))
        ]
    )

    for year_dir in year_dirs:
        month_dirs = sorted(
            [
                os.path.join(year_dir, path_name)
                for path_name in os.listdir(year_dir)
                if os.path.isdir(os.path.join(year_dir, path_name))
                and is_visible_path(os.path.join(year_dir, path_name))
            ]
        )

        for month_dir in month_dirs:
            month_label = os.path.basename(month_dir).replace("all_for_", "")[:7]
            yield month_label, month_dir



def iter_gzip_csv_files(month_dir: str) -> Iterator[str]:
    """
    Yield CSV and compressed CSV files from a month directory.
    This helps keep file discovery separate from stage logic while supporting bundled local samples.
    """

    for pattern in ("*.csv", "*.csv.gz"):
        yield from sorted(
            path for path in glob.glob(os.path.join(month_dir, pattern)) if is_visible_path(path)
        )



def read_lightcast_chunks(
        file_path: str,
        usecols: list[str],
        chunk_size: int,
    ) -> Iterator[pd.DataFrame]:
    """
    Read a compressed Lightcast CSV file in chunks.
    This helps keep memory usage bounded while preserving a pure pandas workflow.
    """

    yield from pd.read_csv(
        file_path,
        compression = "gzip" if file_path.endswith(".gz") else None,
        usecols = usecols,
        dtype = "string",
        chunksize = chunk_size,
        low_memory = False,
    )



def read_csv_exports(export_dir: str) -> Iterator[str]:
    """
    Yield CSV exports from a stage output directory.
    This helps chaining stage outputs without hard-coding filenames.
    """

    yield from sorted(path for path in glob.glob(os.path.join(export_dir, "*.csv")) if is_visible_path(path))
