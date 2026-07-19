"""
AIgnition Backend — Pydantic Request Models
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ──────────────────────────────────────────────────────────────────────────────
# Upload
# ──────────────────────────────────────────────────────────────────────────────
class UploadSource(BaseModel):
    """Optional metadata sent alongside the file upload."""
    source: Optional[Literal["google_ads", "meta_ads", "microsoft_ads", "ga4", "shopify"]] = None


# ──────────────────────────────────────────────────────────────────────────────
# Validate
# ──────────────────────────────────────────────────────────────────────────────
class ValidateRequest(BaseModel):
    upload_id: str = Field(..., description="ID returned by POST /upload")


# ──────────────────────────────────────────────────────────────────────────────
# Forecast
# ──────────────────────────────────────────────────────────────────────────────
class ForecastRequest(BaseModel):
    upload_id: str = Field(..., description="ID returned by POST /upload")
    horizon_days: int = Field(default=30, ge=1, le=365, description="Forecast window in days")


# ──────────────────────────────────────────────────────────────────────────────
# Optimizer
# ──────────────────────────────────────────────────────────────────────────────
class OptimizerRequest(BaseModel):
    upload_id: str = Field(..., description="ID returned by POST /upload")
    total_budget: float = Field(..., gt=0, description="Total monthly budget in USD")
    min_channel_pct: float = Field(default=3.0, ge=0, le=100, description="Minimum % per channel")
    max_channel_pct: float = Field(default=40.0, ge=0, le=100, description="Maximum % per channel")
    roas_floor: float = Field(default=2.0, ge=0, description="Minimum acceptable ROAS")

    @field_validator("max_channel_pct")
    @classmethod
    def max_must_exceed_min(cls, v, info):
        if "min_channel_pct" in info.data and v <= info.data["min_channel_pct"]:
            raise ValueError("max_channel_pct must be greater than min_channel_pct")
        return v


# ──────────────────────────────────────────────────────────────────────────────
# Risks
# ──────────────────────────────────────────────────────────────────────────────
class RisksRequest(BaseModel):
    upload_id: str = Field(..., description="ID returned by POST /upload")


# ──────────────────────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────────────────────
class SummaryRequest(BaseModel):
    upload_id: str = Field(..., description="ID returned by POST /upload")
    forecast: Optional[dict] = Field(default=None, description="Forecast JSON (optional, re-fetched if absent)")
    optimizer: Optional[dict] = Field(default=None)
    risks: Optional[list] = Field(default=None)


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────────────────────
class DashboardRequest(BaseModel):
    upload_id: str = Field(..., description="ID returned by POST /upload")
    total_budget: float = Field(default=420000.0, gt=0)
    horizon_days: int = Field(default=30, ge=1, le=365)
