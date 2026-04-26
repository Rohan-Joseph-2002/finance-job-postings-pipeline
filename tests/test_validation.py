"""
AUTHOR: Rohan Joseph
PURPOSE: Tests for shared schema validation helpers.
DATE CREATED: 2026-04-25
DATE MODIFIED: 2026-04-25
MODIFIED BY: Rohan Joseph
"""



"""
Importing Libraries and Utilities
"""

# --- Import standard libraries ---
import pandas as pd
import pytest


# --- Import project-specific utilities and pipeline code ---
from project.validation import require_columns



"""
Tests
"""


def test_require_columns_raises_on_missing_columns():
    """
    Test that require columns raises on missing columns.
    This helps lock in the expected behavior when the surrounding pipeline changes.
    """
    df = pd.DataFrame({"id": [1]})

    with pytest.raises(ValueError):
        require_columns(df, ["id", "title_clean"], "test dataframe")
