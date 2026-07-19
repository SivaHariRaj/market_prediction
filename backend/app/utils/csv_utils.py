"""
CSV parsing and schema detection utilities for AIgnition backend.

Supports these ad-platform schemas:
  - Google Ads
  - Meta Ads
  - Microsoft Ads
  - GA4
  - Shopify
"""
import re
from pathlib import Path
from typing import Any

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Column alias maps — normalise platform-specific column names to a
# canonical internal schema.
# ---------------------------------------------------------------------------
PLATFORM_COLUMN_ALIASES: dict[str, dict[str, str]] = {
    "google_ads": {
        "campaign": "campaign_name",
        "cost": "spend",
        "conv. value": "revenue",
        "conversions": "conversions",
        "clicks": "clicks",
        "impressions": "impressions",
        "day": "date",
    },
    "meta_ads": {
        "campaign name": "campaign_name",
        "amount spent (usd)": "spend",
        "purchase roas (return on ad spend)": "roas",
        "purchases conversion value": "revenue",
        "date start": "date",
    },
    "microsoft_ads": {
        "campaign": "campaign_name",
        "spend": "spend",
        "revenue": "revenue",
        "day": "date",
    },
    "ga4": {
        "session default channel group": "channel",
        "sessions": "sessions",
        "total revenue": "revenue",
        "date": "date",
    },
    "shopify": {
        "order date": "date",
        "total sales": "revenue",
        "orders": "conversions",
        "channel": "channel",
    },
}

CANONICAL_COLUMNS = {"date", "campaign_name", "spend", "revenue", "roas", "channel"}

DATE_PATTERNS = [
    r"^\d{4}-\d{2}-\d{2}$",          # ISO 8601
    r"^\d{2}/\d{2}/\d{4}$",          # MM/DD/YYYY
    r"^\d{2}-\d{2}-\d{4}$",          # MM-DD-YYYY
    r"^\d{4}/\d{2}/\d{2}$",          # YYYY/MM/DD
]


def detect_platform(columns: list[str]) -> str:
    """Heuristically guess which ad platform produced the CSV."""
    cols_lower = {c.lower() for c in columns}
    if "amount spent (usd)" in cols_lower or "purchase roas (return on ad spend)" in cols_lower:
        return "meta_ads"
    if "conv. value" in cols_lower:
        return "google_ads"
    if "session default channel group" in cols_lower:
        return "ga4"
    if "order date" in cols_lower and "total sales" in cols_lower:
        return "shopify"
    return "microsoft_ads"


def normalise_columns(df: pd.DataFrame, platform: str) -> pd.DataFrame:
    """Rename platform-specific columns to canonical names."""
    alias_map = PLATFORM_COLUMN_ALIASES.get(platform, {})
    rename = {col: alias_map[col.lower()] for col in df.columns if col.lower() in alias_map}
    return df.rename(columns=rename)


def load_csv(path: Path) -> pd.DataFrame:
    """Load a CSV from disk and return a DataFrame."""
    try:
        df = pd.read_csv(path, low_memory=False)
        logger.info("Loaded CSV: %s rows, %s columns", len(df), len(df.columns))
        return df
    except Exception as exc:
        logger.error("Failed to read CSV at %s: %s", path, exc)
        raise ValueError(f"Cannot parse CSV: {exc}") from exc


def is_valid_date(value: Any) -> bool:
    """Check if a scalar value matches any expected date pattern."""
    s = str(value).strip()
    return any(re.match(p, s) for p in DATE_PATTERNS)


def dataframe_summary(df: pd.DataFrame) -> dict:
    """Return basic summary stats for a dataframe."""
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "column_count": len(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }
