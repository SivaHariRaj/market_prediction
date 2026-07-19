"""
AIgnition Backend — ML Interface

This module is the ONLY file the ML team needs to modify.

Replace each `raise NotImplementedError(...)` with the real implementation.
The function signatures and return shapes are the contract — do not change them.
"""
from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# FORECAST
# ──────────────────────────────────────────────────────────────────────────────

def predict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Generate a probabilistic revenue & ROAS forecast.

    Args:
        data: Normalised marketing data dict with keys:
              - "records": list of row dicts (date, channel, spend, revenue, …)
              - "horizon_days": int — forecast window (default 30)
              - "upload_id": str

    Returns:
        {
          "revenue_forecast": {
              "expected": float,
              "uplift_pct": float,
              "p10": float,
              "p50": float,
              "p90": float,
              "confidence": float,          # 0-100
              "mape": float,
              "rmse": float,
          },
          "roas_forecast": {
              "expected": float,
              "p10": float,
              "p50": float,
              "p90": float,
          },
          "series": [                       # daily time-series
              {"date": "MM-DD", "p10": float, "p50": float, "p90": float,
               "actual": float | None},
              ...
          ],
          "channel_forecast": [
              {"channel": str, "spend": float, "revenue": float, "roas": float},
              ...
          ],
          "campaign_forecast": [
              {"campaign": str, "spend": float, "revenue": float, "roas": float},
              ...
          ],
        }

    Raises:
        NotImplementedError: ML team has not yet implemented this function.
    """
    raise NotImplementedError(
        "predict() — ML team will implement this function in ml_interface.py"
    )


# ──────────────────────────────────────────────────────────────────────────────
# SUMMARY / LLM
# ──────────────────────────────────────────────────────────────────────────────

def generate_summary(data: dict[str, Any]) -> dict[str, Any]:
    """
    Generate an executive summary using an LLM.

    Args:
        data: Combined dict with keys:
              - "forecast": output of predict()
              - "optimizer": output of optimizer logic
              - "risks": list of risk dicts

    Returns:
        {
          "executive_summary": str,
          "recommendations": list[str],
          "key_drivers": list[str],
          "confidence_explanation": str,
          "risk_explanation": str,
        }

    Raises:
        NotImplementedError: LLM team has not yet implemented this function.
    """
    raise NotImplementedError(
        "generate_summary() — LLM team will implement this function in ml_interface.py"
    )
