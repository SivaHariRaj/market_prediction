"""
AIgnition — Optimizer Service

Rule-based budget allocation across advertising channels.
Allocates budget using ROAS-weighted proportional splitting, clamped
to min/max constraints. The ML team can replace this logic entirely
by implementing predict() in ml_interface.py and calling it from here.
"""
import pandas as pd

from app.models.response_models import ChannelAllocation, OptimizerResponse
from app.utils.csv_utils import detect_platform, load_csv, normalise_columns
from app.utils.exceptions import UploadNotFound
from app.utils.file_utils import find_upload_file
from app.utils.logger import get_logger

logger = get_logger(__name__)

CHANNEL_COLORS = {
    "google search": "var(--brand)",
    "meta ads": "var(--brand-2)",
    "tiktok": "var(--success)",
    "youtube": "var(--warning)",
    "programmatic": "var(--danger)",
    "affiliate": "oklch(0.55 0.12 240)",
    "microsoft ads": "oklch(0.50 0.13 260)",
}

# Default channel weights when CSV has no channel breakdown
_DEFAULT_CHANNELS = [
    {"name": "Google Search",  "current_pct": 32, "roas": 4.2},
    {"name": "Meta Ads",       "current_pct": 28, "roas": 3.1},
    {"name": "TikTok",         "current_pct": 14, "roas": 3.8},
    {"name": "YouTube",        "current_pct": 12, "roas": 2.9},
    {"name": "Programmatic",   "current_pct": 9,  "roas": 1.8},
    {"name": "Affiliate",      "current_pct": 5,  "roas": 2.4},
]


def run_optimizer(
    upload_id: str,
    total_budget: float,
    min_channel_pct: float = 3.0,
    max_channel_pct: float = 40.0,
    roas_floor: float = 2.0,
) -> OptimizerResponse:
    """
    Allocate total_budget across channels using ROAS-weighted proportional splits.

    Algorithm:
      1. Load channel → ROAS mapping from CSV (or use defaults).
      2. Zero out channels below roas_floor.
      3. Compute ROAS-weighted proportions.
      4. Clamp each channel to [min_channel_pct, max_channel_pct].
      5. Re-normalise to 100%.
      6. Project expected revenue = sum(budget_i * roas_i).
    """
    path = find_upload_file(upload_id)
    if path is None:
        raise UploadNotFound(upload_id)

    df = load_csv(path)
    platform = detect_platform(list(df.columns))
    df = normalise_columns(df, platform)

    # ── Build channel summary from data ────────────────────────────────────
    channel_rows = _extract_channel_summary(df)

    # ── Apply ROAS floor ───────────────────────────────────────────────────
    eligible = [c for c in channel_rows if c["roas"] >= roas_floor]
    if not eligible:
        eligible = channel_rows  # never cut all channels

    # ── ROAS-weighted allocation ────────────────────────────────────────────
    total_roas = sum(c["roas"] for c in eligible)
    for c in eligible:
        raw_pct = (c["roas"] / total_roas) * 100
        c["optimized_pct"] = max(min_channel_pct, min(max_channel_pct, raw_pct))

    # Channels below floor get min_channel_pct
    excluded = [c for c in channel_rows if c not in eligible]
    for c in excluded:
        c["optimized_pct"] = min_channel_pct

    # Re-normalise to 100
    total_pct = sum(c["optimized_pct"] for c in channel_rows)
    for c in channel_rows:
        c["optimized_pct"] = round(c["optimized_pct"] / total_pct * 100, 2)

    # ── Compute budgets and expected revenue ────────────────────────────────
    allocations: list[ChannelAllocation] = []
    expected_revenue = 0.0
    google_budget = meta_budget = microsoft_budget = 0.0
    other_budgets: dict[str, float] = {}

    for c in channel_rows:
        opt_budget = round(total_budget * c["optimized_pct"] / 100, 2)
        cur_budget = round(total_budget * c["current_pct"] / 100, 2)
        rev = opt_budget * c["roas"]
        expected_revenue += rev

        name_lower = c["name"].lower()
        if "google" in name_lower:
            google_budget += opt_budget
        elif "meta" in name_lower or "facebook" in name_lower:
            meta_budget += opt_budget
        elif "microsoft" in name_lower or "bing" in name_lower:
            microsoft_budget += opt_budget
        else:
            other_budgets[c["name"]] = round(opt_budget + other_budgets.get(c["name"], 0), 2)

        allocations.append(
            ChannelAllocation(
                channel=c["name"],
                current_pct=c["current_pct"],
                optimized_pct=c["optimized_pct"],
                current_budget=cur_budget,
                optimized_budget=opt_budget,
                delta_pct=round(c["optimized_pct"] - c["current_pct"], 2),
                roas=c["roas"],
                color=CHANNEL_COLORS.get(name_lower, "#94a3b8"),
            )
        )

    current_revenue = sum(
        total_budget * c["current_pct"] / 100 * c["roas"] for c in channel_rows
    )
    expected_roas = round(expected_revenue / max(total_budget, 1), 2)
    uplift_pct = round((expected_revenue - current_revenue) / max(current_revenue, 1) * 100, 1)

    logger.info(
        "Optimizer complete for %s — budget=%.0f expected_rev=%.0f uplift=%.1f%%",
        upload_id, total_budget, expected_revenue, uplift_pct,
    )

    return OptimizerResponse(
        upload_id=upload_id,
        total_budget=total_budget,
        google_budget=round(google_budget, 2),
        meta_budget=round(meta_budget, 2),
        microsoft_budget=round(microsoft_budget, 2),
        other_budgets=other_budgets,
        expected_revenue=round(expected_revenue, 2),
        expected_roas=expected_roas,
        estimated_uplift_pct=uplift_pct,
        channels=allocations,
        strategy={
            "total_budget_cap": total_budget,
            "min_channel_pct": min_channel_pct,
            "max_channel_pct": max_channel_pct,
            "roas_floor": roas_floor,
            "solver": "ROAS-weighted proportional (rule-based)",
        },
    )


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _extract_channel_summary(df: pd.DataFrame) -> list[dict]:
    """
    Extract per-channel spend, revenue, and ROAS from the dataframe.
    Falls back to hard-coded defaults when the necessary columns are absent.
    """
    has_channel = "channel" in df.columns or "campaign_name" in df.columns
    has_spend = "spend" in df.columns
    has_revenue = "revenue" in df.columns

    if has_channel and has_spend and has_revenue:
        group_col = "channel" if "channel" in df.columns else "campaign_name"
        df["spend"] = pd.to_numeric(df["spend"], errors="coerce").fillna(0)
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)
        agg = df.groupby(group_col).agg(spend=("spend", "sum"), revenue=("revenue", "sum")).reset_index()
        agg["roas"] = (agg["revenue"] / agg["spend"].replace(0, float("nan"))).fillna(2.0).round(2)
        total_spend = agg["spend"].sum()
        result = []
        for _, row in agg.iterrows():
            result.append({
                "name": str(row[group_col]),
                "current_pct": round(row["spend"] / max(total_spend, 1) * 100, 2),
                "roas": float(row["roas"]),
            })
        return result[:8]  # cap at 8 channels for display

    # Default
    return [dict(c) for c in _DEFAULT_CHANNELS]
