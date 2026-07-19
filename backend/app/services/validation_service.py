"""
AIgnition — Validation Service
Runs data-quality checks on an uploaded CSV.
"""
import math
from pathlib import Path

import numpy as np
import pandas as pd

from app.models.response_models import ValidateResponse, ValidationIssue
from app.utils.csv_utils import detect_platform, is_valid_date, load_csv, normalise_columns
from app.utils.exceptions import InvalidCSV, UploadNotFound
from app.utils.file_utils import find_upload_file
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Quality score weights (must sum to 100)
WEIGHTS = {
    "duplicates": 15,
    "missing_campaigns": 15,
    "missing_values": 20,
    "invalid_roas": 10,
    "revenue_spikes": 10,
    "invalid_dates": 15,
    "negative_revenue": 15,
}

SPIKE_THRESHOLD = 4.0  # standard deviations


def _issue_empty() -> ValidationIssue:
    return ValidationIssue(row_indices=[], count=0, examples=[])


def run_validation(upload_id: str) -> ValidateResponse:
    """
    Execute all data-quality checks and compute a 0-100 quality score.
    """
    # ── Locate file ───────────────────────────────────────────────────────
    path = find_upload_file(upload_id)
    if path is None:
        raise UploadNotFound(upload_id)

    try:
        df = load_csv(path)
    except ValueError as exc:
        raise InvalidCSV(str(exc)) from exc

    platform = detect_platform(list(df.columns))
    df = normalise_columns(df, platform)

    issues: dict[str, ValidationIssue] = {k: _issue_empty() for k in WEIGHTS}
    warnings: list[str] = []
    penalty = 0.0

    total_rows = len(df)

    # ── 1. Duplicate rows ─────────────────────────────────────────────────
    dup_mask = df.duplicated()
    dup_count = int(dup_mask.sum())
    if dup_count:
        idx = list(df.index[dup_mask][:5])
        issues["duplicates"] = ValidationIssue(row_indices=idx, count=dup_count, examples=[])
        penalty += WEIGHTS["duplicates"] * min(1.0, dup_count / max(total_rows, 1))
        warnings.append(f"{dup_count} duplicate rows detected — these will be dropped before modelling.")

    # ── 2. Missing campaign names ─────────────────────────────────────────
    if "campaign_name" in df.columns:
        miss_mask = df["campaign_name"].isna() | (df["campaign_name"].astype(str).str.strip() == "")
        miss_count = int(miss_mask.sum())
        if miss_count:
            issues["missing_campaigns"] = ValidationIssue(
                row_indices=list(df.index[miss_mask][:5]),
                count=miss_count,
                examples=[],
            )
            penalty += WEIGHTS["missing_campaigns"] * min(1.0, miss_count / max(total_rows, 1))
            warnings.append(f"{miss_count} rows have no campaign name.")

    # ── 3. Missing values (any column) ────────────────────────────────────
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    if total_nulls:
        top_cols = null_counts[null_counts > 0].nlargest(3).index.tolist()
        issues["missing_values"] = ValidationIssue(
            row_indices=[],
            count=total_nulls,
            examples=[f"{col}: {int(null_counts[col])} nulls" for col in top_cols],
        )
        null_pct = total_nulls / max(df.size, 1)
        penalty += WEIGHTS["missing_values"] * min(1.0, null_pct * 10)
        if null_pct > 0.05:
            warnings.append(f"{null_pct*100:.1f}% of values are missing — imputation recommended.")

    # ── 4. Invalid ROAS ───────────────────────────────────────────────────
    if "roas" in df.columns:
        roas_col = pd.to_numeric(df["roas"], errors="coerce")
        bad_roas = roas_col[(roas_col < 0) | (roas_col > 100)]
        if len(bad_roas):
            issues["invalid_roas"] = ValidationIssue(
                row_indices=list(bad_roas.index[:5]),
                count=len(bad_roas),
                examples=[f"ROAS={v:.2f}" for v in bad_roas.values[:3]],
            )
            penalty += WEIGHTS["invalid_roas"]
            warnings.append(f"{len(bad_roas)} rows have ROAS outside [0, 100].")

    # ── 5. Revenue spikes ─────────────────────────────────────────────────
    if "revenue" in df.columns:
        rev = pd.to_numeric(df["revenue"], errors="coerce").dropna()
        if len(rev) > 5:
            mean, std = rev.mean(), rev.std()
            spike_mask = (rev - mean).abs() > SPIKE_THRESHOLD * std
            spike_count = int(spike_mask.sum())
            if spike_count:
                issues["revenue_spikes"] = ValidationIssue(
                    row_indices=list(rev.index[spike_mask][:5]),
                    count=spike_count,
                    examples=[f"${v:,.0f}" for v in rev[spike_mask].values[:3]],
                )
                penalty += WEIGHTS["revenue_spikes"] * 0.5
                warnings.append(f"{spike_count} revenue spikes detected (>{SPIKE_THRESHOLD}σ).")

    # ── 6. Date format ────────────────────────────────────────────────────
    date_col = next((c for c in df.columns if c in ("date", "day", "date start", "order date")), None)
    if date_col:
        sample = df[date_col].dropna().astype(str).head(50)
        bad_dates = [v for v in sample if not is_valid_date(v)]
        if bad_dates:
            issues["invalid_dates"] = ValidationIssue(
                row_indices=[],
                count=len(bad_dates),
                examples=bad_dates[:3],
            )
            penalty += WEIGHTS["invalid_dates"] * min(1.0, len(bad_dates) / max(len(sample), 1))
            warnings.append("Some date values do not match expected formats (YYYY-MM-DD, MM/DD/YYYY, etc.).")

    # ── 7. Negative revenue ───────────────────────────────────────────────
    if "revenue" in df.columns:
        rev_col = pd.to_numeric(df["revenue"], errors="coerce")
        neg_mask = rev_col < 0
        neg_count = int(neg_mask.sum())
        if neg_count:
            issues["negative_revenue"] = ValidationIssue(
                row_indices=list(df.index[neg_mask][:5]),
                count=neg_count,
                examples=[f"${v:,.2f}" for v in rev_col[neg_mask].values[:3]],
            )
            penalty += WEIGHTS["negative_revenue"]
            warnings.append(f"{neg_count} rows have negative revenue.")

    # ── Quality score ─────────────────────────────────────────────────────
    quality_score = max(0.0, round(100.0 - penalty, 1))
    passed = quality_score >= 70.0

    # ── Build step list for frontend animation ────────────────────────────
    steps = [
        {"label": "Schema check", "detail": f"{total_rows} rows · {len(df.columns)} columns", "passed": True},
        {"label": "Duplicate rows", "detail": f"{issues['duplicates'].count} found", "passed": issues["duplicates"].count == 0},
        {"label": "Missing campaign names", "detail": f"{issues['missing_campaigns'].count} rows affected", "passed": issues["missing_campaigns"].count == 0},
        {"label": "Missing values", "detail": f"{issues['missing_values'].count} total nulls", "passed": issues["missing_values"].count == 0},
        {"label": "ROAS validity", "detail": f"{issues['invalid_roas'].count} invalid values", "passed": issues["invalid_roas"].count == 0},
        {"label": "Revenue spike detection", "detail": f"{issues['revenue_spikes'].count} spikes", "passed": issues["revenue_spikes"].count == 0},
        {"label": "Date format", "detail": f"{issues['invalid_dates'].count} invalid dates", "passed": issues["invalid_dates"].count == 0},
        {"label": "Negative revenue", "detail": f"{issues['negative_revenue'].count} rows", "passed": issues["negative_revenue"].count == 0},
    ]

    logger.info(
        "Validation complete for %s — score=%.1f passed=%s",
        upload_id, quality_score, passed,
    )

    return ValidateResponse(
        upload_id=upload_id,
        quality_score=quality_score,
        passed=passed,
        duplicates=issues["duplicates"],
        missing_campaigns=issues["missing_campaigns"],
        missing_values=issues["missing_values"],
        invalid_roas=issues["invalid_roas"],
        revenue_spikes=issues["revenue_spikes"],
        invalid_dates=issues["invalid_dates"],
        negative_revenue=issues["negative_revenue"],
        warnings=warnings,
        steps=steps,
    )
