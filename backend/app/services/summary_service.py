"""
AIgnition — Summary Service

Calls ml_interface.generate_summary().
Falls back to a rule-based template when the LLM is not yet implemented.
The LLM team only needs to implement generate_summary() in ml_interface.py.
"""
from app import ml_interface
from app.config import settings
from app.models.response_models import SummaryResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


def run_summary(
    upload_id: str,
    forecast: dict | None = None,
    optimizer: dict | None = None,
    risks: list | None = None,
) -> SummaryResponse:
    """
    Generate an executive summary.

    1. Tries ml_interface.generate_summary() first.
    2. Falls back to _template_summary() if NotImplementedError is raised.
    """
    data = {
        "forecast": forecast or {},
        "optimizer": optimizer or {},
        "risks": risks or [],
    }

    is_llm = False
    try:
        result = ml_interface.generate_summary(data)
        is_llm = True
        logger.info("LLM generate_summary() returned results for upload %s", upload_id)
        return SummaryResponse(
            upload_id=upload_id,
            is_llm=True,
            **result,
        )
    except NotImplementedError:
        if not settings.ML_FALLBACK_ENABLED:
            raise
        logger.warning(
            "ml_interface.generate_summary() not implemented — using template fallback for %s",
            upload_id,
        )
        return _template_summary(upload_id, forecast, optimizer, risks)


def generate_summary(data: dict) -> dict:
    """
    Placeholder hook — LLM team will replace this in ml_interface.py.
    Kept here as a service-layer convenience wrapper.
    """
    raise NotImplementedError(
        "generate_summary() — LLM team will implement this in ml_interface.py"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Template fallback
# ──────────────────────────────────────────────────────────────────────────────

def _template_summary(
    upload_id: str,
    forecast: dict | None,
    optimizer: dict | None,
    risks: list | None,
) -> SummaryResponse:
    """
    Build a structured summary from rule-based data when LLM is unavailable.
    Dynamically populates values from the forecast / optimizer / risks dicts.
    """
    # Pull key values with safe fallbacks
    rev = _deep_get(forecast, "revenue_forecast", "expected") or 1_284_000
    uplift = _deep_get(forecast, "revenue_forecast", "uplift_pct") or 12.4
    roas = _deep_get(forecast, "roas_forecast", "expected") or 3.7
    confidence = _deep_get(forecast, "revenue_forecast", "confidence") or 87

    total_budget = _deep_get(optimizer, "total_budget") or 420_000
    risk_list = risks or []
    risk_flags = sum(1 for r in risk_list if r.get("severity") == "risk")
    watch_flags = sum(1 for r in risk_list if r.get("severity") == "watch")

    executive_summary = (
        f"Over the next 30 days, AIgnition projects ${rev:,.0f} in revenue "
        f"at {roas:.1f}x blended ROAS — a +{uplift:.1f}% lift versus current pacing, "
        f"with {confidence:.0f}% model confidence. "
        f"The dataset shows {risk_flags} active risk flag(s) and {watch_flags} watch signal(s)."
    )

    recommendations = [
        "Apply the AI-optimised budget allocation to maximise expected revenue.",
        "Refresh creatives on channels showing CTR decline within 7 days.",
        "Monitor channels below the 2.0x ROAS floor and reduce spend if decline continues.",
        f"Keep total monthly budget near ${total_budget:,.0f} to maintain forecast accuracy.",
    ]

    top_risks = [r.get("title", "") for r in risk_list if r.get("severity") == "risk"][:3]

    key_drivers = [
        f"ROAS-weighted reallocation is the primary revenue lever ({uplift:.1f}% projected lift).",
        "Channels with ROAS > 3.5x are driving outsized returns.",
        "Creative freshness is a secondary driver — higher CTR improves channel efficiency.",
    ]

    confidence_explanation = (
        f"The {confidence:.0f}% confidence figure represents ensemble agreement across multiple "
        "forecasting signals. A score above 80% indicates high reliability for 30-day planning."
    )

    risk_explanation = (
        f"{'No critical risks detected.' if not risk_flags else f'{risk_flags} risk flag(s) detected: ' + ', '.join(top_risks) + '.'} "
        f"{watch_flags} watch signal(s) require monitoring but do not block the recommendation."
    )

    return SummaryResponse(
        upload_id=upload_id,
        is_llm=False,
        executive_summary=executive_summary,
        recommendations=recommendations,
        key_drivers=key_drivers,
        confidence_explanation=confidence_explanation,
        risk_explanation=risk_explanation,
    )


def _deep_get(d: dict | None, *keys, default=None):
    """Safely traverse nested dict keys."""
    if d is None:
        return default
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
    return d
