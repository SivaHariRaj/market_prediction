"""
AIgnition — Forecast Service

This service calls ml_interface.predict().
If the ML model is not yet implemented, it falls back to a
rule-based mock that mirrors the shapes expected by the frontend.
The ML team only needs to implement predict() in ml_interface.py.
"""
import math
import random
from datetime import date, timedelta

import pandas as pd

from app import ml_interface
from app.config import settings
from app.models.response_models import (
    ChannelForecast,
    CampaignForecast,
    ForecastPoint,
    ForecastResponse,
    RevenueForecast,
    ROASForecast,
)
from app.utils.csv_utils import detect_platform, load_csv, normalise_columns
from app.utils.exceptions import UploadNotFound
from app.utils.file_utils import find_upload_file
from app.utils.logger import get_logger

logger = get_logger(__name__)

CHANNEL_COLORS = {
    "google_search": "var(--brand)",
    "meta_ads": "var(--brand-2)",
    "tiktok": "var(--success)",
    "youtube": "var(--warning)",
    "programmatic": "var(--danger)",
    "affiliate": "oklch(0.55 0.12 240)",
    "microsoft_ads": "oklch(0.50 0.13 260)",
    "other": "#94a3b8",
}


# ──────────────────────────────────────────────────────────────────────────────
# Public entry-point
# ──────────────────────────────────────────────────────────────────────────────

def run_forecast(upload_id: str, horizon_days: int = 30) -> ForecastResponse:
    """
    Generate a forecast.
    1. Tries ml_interface.predict() first.
    2. Falls back to _mock_forecast() if NotImplementedError is raised
       (only when settings.ML_FALLBACK_ENABLED is True).
    """
    path = find_upload_file(upload_id)
    if path is None:
        raise UploadNotFound(upload_id)

    df = load_csv(path)
    platform = detect_platform(list(df.columns))
    df = normalise_columns(df, platform)

    data = {
        "records": df.to_dict(orient="records"),
        "horizon_days": horizon_days,
        "upload_id": upload_id,
    }

    is_ml = False
    try:
        result = ml_interface.predict(data)
        is_ml = True
        logger.info("ML predict() returned results for upload %s", upload_id)
        return _build_from_ml(upload_id, result, is_ml=True)
    except NotImplementedError:
        if not settings.ML_FALLBACK_ENABLED:
            raise
        logger.warning(
            "ml_interface.predict() not implemented — using rule-based fallback for %s",
            upload_id,
        )
        return _mock_forecast(upload_id, df, horizon_days)


# ──────────────────────────────────────────────────────────────────────────────
# ML result → response model
# ──────────────────────────────────────────────────────────────────────────────

def _build_from_ml(upload_id: str, result: dict, is_ml: bool = True) -> ForecastResponse:
    rf = result["revenue_forecast"]
    roas = result["roas_forecast"]
    return ForecastResponse(
        upload_id=upload_id,
        is_ml=is_ml,
        revenue_forecast=RevenueForecast(**rf),
        roas_forecast=ROASForecast(**roas),
        series=[ForecastPoint(**p) for p in result["series"]],
        channel_forecast=[ChannelForecast(**c) for c in result["channel_forecast"]],
        campaign_forecast=[CampaignForecast(**c) for c in result["campaign_forecast"]],
    )


# ──────────────────────────────────────────────────────────────────────────────
# Rule-based fallback (replaces the static mock-data.ts values)
# ──────────────────────────────────────────────────────────────────────────────

def _seeded_rand(seed: int = 42):
    rng = random.Random(seed)
    return rng.random


def _mock_forecast(upload_id: str, df: pd.DataFrame, horizon_days: int) -> ForecastResponse:
    """
    Deterministic rule-based fallback that matches the frontend ForecastPoint shape.
    Uses actual data from the CSV when available, otherwise uses sensible defaults.
    """
    rand = _seeded_rand(42)

    # ── Derive actuals from CSV ────────────────────────────────────────────
    base_revenue = 42_000.0
    if "revenue" in df.columns:
        rev = pd.to_numeric(df["revenue"], errors="coerce").dropna()
        if len(rev):
            base_revenue = float(rev.mean())

    # ── Build time series (30 days actual + horizon forward) ──────────────
    history_days = 30
    total_days = history_days + horizon_days
    start = date.today() - timedelta(days=history_days)
    series: list[ForecastPoint] = []

    for i in range(total_days):
        d = start + timedelta(days=i)
        trend = i * (base_revenue * 0.005)
        season = math.sin((i / 7) * math.pi) * (base_revenue * 0.1)
        noise = (rand() - 0.5) * (base_revenue * 0.07)
        p50 = max(0.0, base_revenue + trend + season + noise)
        spread = base_revenue * 0.1 + i * (base_revenue * 0.002)
        point = ForecastPoint(
            date=d.strftime("%m-%d"),
            p10=max(0.0, p50 - spread),
            p50=round(p50, 2),
            p90=round(p50 + spread, 2),
            actual=round(p50 + (rand() - 0.5) * (base_revenue * 0.05), 2) if i < history_days else None,
        )
        series.append(point)

    p50_forward = [s.p50 for s in series[history_days:]]
    expected_revenue = sum(p50_forward)
    baseline_revenue = expected_revenue * 0.885  # 12.4% uplift baseline
    uplift = round((expected_revenue - baseline_revenue) / baseline_revenue * 100, 1)

    # ── Channel breakdown ─────────────────────────────────────────────────
    channel_data = [
        {"channel": "Google Search", "key": "google_search", "current_pct": 32, "optimized_pct": 38, "roas": 4.2},
        {"channel": "Meta Ads",      "key": "meta_ads",      "current_pct": 28, "optimized_pct": 24, "roas": 3.1},
        {"channel": "TikTok",        "key": "tiktok",        "current_pct": 14, "optimized_pct": 18, "roas": 3.8},
        {"channel": "YouTube",       "key": "youtube",       "current_pct": 12, "optimized_pct": 11, "roas": 2.9},
        {"channel": "Programmatic",  "key": "programmatic",  "current_pct": 9,  "optimized_pct": 6,  "roas": 1.8},
        {"channel": "Affiliate",     "key": "affiliate",     "current_pct": 5,  "optimized_pct": 3,  "roas": 2.4},
    ]

    total_spend_est = expected_revenue / 3.7  # implied from ROAS
    channels = [
        ChannelForecast(
            channel=c["channel"],
            spend=round(total_spend_est * c["current_pct"] / 100, 2),
            revenue=round(total_spend_est * c["current_pct"] / 100 * c["roas"], 2),
            roas=c["roas"],
            current_pct=c["current_pct"],
            optimized_pct=c["optimized_pct"],
            color=CHANNEL_COLORS.get(c["key"], CHANNEL_COLORS["other"]),
        )
        for c in channel_data
    ]

    # ── Campaign breakdown ────────────────────────────────────────────────
    if "campaign_name" in df.columns and "spend" in df.columns and "revenue" in df.columns:
        cdf = df.groupby("campaign_name").agg(
            spend=("spend", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()
        cdf["roas"] = (cdf["revenue"] / cdf["spend"].replace(0, float("nan"))).fillna(0).round(2)
        campaigns = [
            CampaignForecast(
                campaign=str(row["campaign_name"]),
                spend=round(float(row["spend"]), 2),
                revenue=round(float(row["revenue"]), 2),
                roas=round(float(row["roas"]), 2),
            )
            for _, row in cdf.head(10).iterrows()
        ]
    else:
        campaigns = [
            CampaignForecast(campaign="Brand Search",       spend=62_000,  revenue=260_400, roas=4.2),
            CampaignForecast(campaign="Retargeting",        spend=48_000,  revenue=153_600, roas=3.2),
            CampaignForecast(campaign="Prospecting - Meta", spend=55_000,  revenue=170_500, roas=3.1),
            CampaignForecast(campaign="TikTok UGC",         spend=28_000,  revenue=106_400, roas=3.8),
        ]

    return ForecastResponse(
        upload_id=upload_id,
        is_ml=False,
        revenue_forecast=RevenueForecast(
            expected=round(expected_revenue, 2),
            uplift_pct=uplift,
            p10=round(expected_revenue * 0.88, 2),
            p50=round(expected_revenue, 2),
            p90=round(expected_revenue * 1.12, 2),
            confidence=87.0,
            mape=6.2,
            rmse=4180.0,
        ),
        roas_forecast=ROASForecast(
            expected=3.7,
            p10=3.1,
            p50=3.7,
            p90=4.3,
        ),
        series=series,
        channel_forecast=channels,
        campaign_forecast=campaigns,
    )
