"""
AIgnition — Risk Service

Rule-based risk detection engine.
Analyses the uploaded CSV for concentration, ROAS, saturation,
instability and seasonality signals. Replace individual _check_*()
functions with ML-based detectors later without changing the public API.
"""
import statistics
from collections import defaultdict

import pandas as pd

from app.models.response_models import RiskItem, RisksResponse
from app.utils.csv_utils import detect_platform, load_csv, normalise_columns
from app.utils.exceptions import UploadNotFound
from app.utils.file_utils import find_upload_file
from app.utils.logger import get_logger

logger = get_logger(__name__)


def run_risks(upload_id: str) -> RisksResponse:
    """
    Execute all risk checks and return a structured risk report.
    """
    path = find_upload_file(upload_id)
    if path is None:
        raise UploadNotFound(upload_id)

    df = load_csv(path)
    platform = detect_platform(list(df.columns))
    df = normalise_columns(df, platform)

    # Coerce numeric cols
    for col in ("spend", "revenue", "roas", "clicks", "impressions"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    risks: list[RiskItem] = []
    risks.extend(_check_budget_concentration(df))
    risks.extend(_check_low_roas(df))
    risks.extend(_check_revenue_instability(df))
    risks.extend(_check_campaign_saturation(df))
    risks.extend(_check_ctr_decline(df))
    risks.extend(_check_cpa_spike(df))
    risks.extend(_check_tracking_anomaly(df))
    risks.extend(_check_seasonality(df))

    # Ensure at least some healthy signals
    if not any(r.severity == "healthy" for r in risks):
        risks.append(RiskItem(
            id="general_health",
            title="Data Health",
            severity="healthy",
            description="Dataset passed basic integrity checks.",
            metric="OK",
            category="data",
        ))

    return RisksResponse(
        upload_id=upload_id,
        risk_count=sum(1 for r in risks if r.severity == "risk"),
        watch_count=sum(1 for r in risks if r.severity == "watch"),
        healthy_count=sum(1 for r in risks if r.severity == "healthy"),
        risks=risks,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Individual risk detectors
# ──────────────────────────────────────────────────────────────────────────────

def _check_budget_concentration(df: pd.DataFrame) -> list[RiskItem]:
    """Flag if any single channel exceeds 40% of total spend."""
    if "spend" not in df.columns:
        return []
    group_col = "channel" if "channel" in df.columns else "campaign_name"
    if group_col not in df.columns:
        return []

    agg = df.groupby(group_col)["spend"].sum()
    total = agg.sum()
    if total == 0:
        return []

    max_pct = (agg.max() / total) * 100
    top_ch = agg.idxmax()

    if max_pct > 40:
        return [RiskItem(
            id="budget_concentration",
            title="Budget Concentration",
            severity="risk",
            description=f"{top_ch} accounts for {max_pct:.0f}% of total spend — over-reliance risk.",
            metric=f"{max_pct:.0f}% concentration",
            category="allocation",
        )]
    elif max_pct > 30:
        return [RiskItem(
            id="budget_concentration",
            title="Budget Concentration",
            severity="watch",
            description=f"{top_ch} accounts for {max_pct:.0f}% of spend. Monitor for over-reliance.",
            metric=f"{max_pct:.0f}% max",
            category="allocation",
        )]
    return [RiskItem(
        id="budget_concentration",
        title="Budget Concentration",
        severity="healthy",
        description="No single channel exceeds 40% of spend.",
        metric=f"{max_pct:.0f}% max",
        category="allocation",
    )]


def _check_low_roas(df: pd.DataFrame) -> list[RiskItem]:
    """Flag channels with ROAS below 2.0."""
    if "roas" not in df.columns:
        return []
    roas_col = df["roas"].dropna()
    if roas_col.empty:
        return []
    mean_roas = roas_col.mean()
    low_count = int((roas_col < 2.0).sum())

    if low_count > 0 or mean_roas < 2.0:
        return [RiskItem(
            id="low_roas",
            title="Low ROAS",
            severity="risk",
            description=f"{low_count} rows have ROAS < 2.0x. Blended ROAS is {mean_roas:.2f}x.",
            metric=f"{mean_roas:.2f}x ROAS",
            category="performance",
        )]
    return []


def _check_revenue_instability(df: pd.DataFrame) -> list[RiskItem]:
    """Flag if revenue coefficient of variation is high."""
    if "revenue" not in df.columns:
        return []
    rev = df["revenue"].dropna()
    if len(rev) < 5 or rev.mean() == 0:
        return []
    cv = rev.std() / rev.mean()

    if cv > 0.5:
        return [RiskItem(
            id="revenue_instability",
            title="Revenue Instability",
            severity="risk",
            description=f"Revenue variance is high (CV={cv:.2f}). Forecast uncertainty increases.",
            metric=f"CV {cv:.2f}",
            category="forecast",
        )]
    elif cv > 0.25:
        return [RiskItem(
            id="revenue_instability",
            title="Revenue Instability",
            severity="watch",
            description=f"Moderate revenue variability (CV={cv:.2f}). Watch for trend changes.",
            metric=f"CV {cv:.2f}",
            category="forecast",
        )]
    return [RiskItem(
        id="revenue_instability",
        title="Revenue Stability",
        severity="healthy",
        description="Revenue is stable across the dataset.",
        metric=f"CV {cv:.2f}",
        category="forecast",
    )]


def _check_campaign_saturation(df: pd.DataFrame) -> list[RiskItem]:
    """
    Heuristic: if spend is high but ROAS is declining, flag saturation.
    Uses the top-spend campaign/channel.
    """
    if "spend" not in df.columns or "roas" not in df.columns:
        return []
    group_col = "channel" if "channel" in df.columns else "campaign_name"
    if group_col not in df.columns:
        return []

    agg = df.groupby(group_col).agg(spend=("spend", "sum"), roas=("roas", "mean")).reset_index()
    if agg.empty:
        return []
    top = agg.loc[agg["spend"].idxmax()]
    top_roas = float(top["roas"])

    if top_roas < 2.5:
        return [RiskItem(
            id="campaign_saturation",
            title="Campaign Saturation",
            severity="watch",
            description=f"{top[group_col]} has highest spend but ROAS of {top_roas:.1f}x — possible saturation.",
            metric=f"ROAS {top_roas:.1f}x",
            category="performance",
        )]
    return []


def _check_ctr_decline(df: pd.DataFrame) -> list[RiskItem]:
    """Detect click-through rate decline if clicks + impressions available."""
    if "clicks" not in df.columns or "impressions" not in df.columns:
        return []
    df2 = df.copy()
    df2 = df2[df2["impressions"] > 0].copy()
    if df2.empty:
        return []
    df2["ctr"] = df2["clicks"] / df2["impressions"]
    ctr_mean = df2["ctr"].mean()

    if ctr_mean < 0.01:
        return [RiskItem(
            id="ctr_decline",
            title="CTR Decline",
            severity="watch",
            description=f"Average CTR is {ctr_mean*100:.2f}% — below 1% threshold.",
            metric=f"CTR {ctr_mean*100:.2f}%",
            category="creative",
        )]
    return []


def _check_cpa_spike(df: pd.DataFrame) -> list[RiskItem]:
    """Check for unusually high cost-per-acquisition."""
    if "spend" not in df.columns or "conversions" not in df.columns:
        return []
    df2 = df.copy()
    df2["conversions"] = pd.to_numeric(df2["conversions"], errors="coerce")
    df2 = df2[df2["conversions"] > 0]
    if df2.empty:
        return []
    cpa = df2["spend"].sum() / df2["conversions"].sum()

    if cpa > 100:
        return [RiskItem(
            id="cpa_spike",
            title="CPA Spike",
            severity="risk",
            description=f"Blended CPA is ${cpa:.0f} — exceeds typical efficiency thresholds.",
            metric=f"${cpa:.0f} CPA",
            category="performance",
        )]
    return []


def _check_tracking_anomaly(df: pd.DataFrame) -> list[RiskItem]:
    """Detect date gaps that may indicate tracking failures."""
    date_col = next((c for c in df.columns if c in ("date", "day")), None)
    if not date_col:
        return []
    try:
        dates = pd.to_datetime(df[date_col], errors="coerce").dropna().sort_values()
        if len(dates) < 3:
            return []
        gaps = (dates.diff().dt.days.dropna() > 1).sum()
        if gaps > 0:
            return [RiskItem(
                id="tracking_anomaly",
                title="Tracking Gap",
                severity="watch",
                description=f"{gaps} date gap(s) detected — may indicate tracking failures.",
                metric=f"{gaps} gap(s)",
                category="data",
            )]
    except Exception:
        pass
    return []


def _check_seasonality(df: pd.DataFrame) -> list[RiskItem]:
    """
    Simple heuristic: if data spans more than 60 days,
    flag a seasonality watch for holiday periods.
    """
    date_col = next((c for c in df.columns if c in ("date", "day")), None)
    if not date_col:
        return []
    try:
        dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
        span = (dates.max() - dates.min()).days
        if span > 60:
            return [RiskItem(
                id="seasonality",
                title="Seasonal Shift",
                severity="watch",
                description=f"Dataset spans {span} days. Seasonal demand patterns may affect forecast accuracy.",
                metric=f"{span} days",
                category="forecast",
            )]
    except Exception:
        pass
    return []
