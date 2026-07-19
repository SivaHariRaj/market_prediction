"""
AIgnition Backend — Pydantic Response Models
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────────────────
# Upload
# ──────────────────────────────────────────────────────────────────────────────
class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    rows: int
    columns: list[str]
    column_count: int
    platform_detected: str
    status: Literal["success", "error"] = "success"
    message: str = "File uploaded and parsed successfully."


# ──────────────────────────────────────────────────────────────────────────────
# Validate
# ──────────────────────────────────────────────────────────────────────────────
class ValidationIssue(BaseModel):
    row_indices: list[int] = Field(default_factory=list)
    count: int = 0
    examples: list[str] = Field(default_factory=list)


class ValidateResponse(BaseModel):
    upload_id: str
    quality_score: float = Field(..., ge=0, le=100, description="Overall data quality 0-100")
    passed: bool
    # Checks
    duplicates: ValidationIssue
    missing_campaigns: ValidationIssue
    missing_values: ValidationIssue
    invalid_roas: ValidationIssue
    revenue_spikes: ValidationIssue
    invalid_dates: ValidationIssue
    negative_revenue: ValidationIssue
    # Warnings
    warnings: list[str] = Field(default_factory=list)
    # Steps (for frontend animation)
    steps: list[dict] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
# Forecast
# ──────────────────────────────────────────────────────────────────────────────
class RevenueForecast(BaseModel):
    expected: float
    uplift_pct: float
    p10: float
    p50: float
    p90: float
    confidence: float = Field(..., ge=0, le=100)
    mape: float
    rmse: float


class ROASForecast(BaseModel):
    expected: float
    p10: float
    p50: float
    p90: float


class ForecastPoint(BaseModel):
    date: str
    p10: float
    p50: float
    p90: float
    actual: Optional[float] = None


class ChannelForecast(BaseModel):
    channel: str
    spend: float
    revenue: float
    roas: float
    current_pct: float
    optimized_pct: float
    color: str


class CampaignForecast(BaseModel):
    campaign: str
    spend: float
    revenue: float
    roas: float


class ForecastResponse(BaseModel):
    upload_id: str
    is_ml: bool = Field(False, description="True when real ML model was used")
    revenue_forecast: RevenueForecast
    roas_forecast: ROASForecast
    series: list[ForecastPoint]
    channel_forecast: list[ChannelForecast]
    campaign_forecast: list[CampaignForecast]


# ──────────────────────────────────────────────────────────────────────────────
# Optimizer
# ──────────────────────────────────────────────────────────────────────────────
class ChannelAllocation(BaseModel):
    channel: str
    current_pct: float
    optimized_pct: float
    current_budget: float
    optimized_budget: float
    delta_pct: float
    roas: float
    color: str


class OptimizerResponse(BaseModel):
    upload_id: str
    total_budget: float
    google_budget: float
    meta_budget: float
    microsoft_budget: float
    other_budgets: dict[str, float] = Field(default_factory=dict)
    expected_revenue: float
    expected_roas: float
    estimated_uplift_pct: float
    channels: list[ChannelAllocation]
    strategy: dict = Field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────────────
# Risks
# ──────────────────────────────────────────────────────────────────────────────
class RiskItem(BaseModel):
    id: str
    title: str
    severity: Literal["healthy", "watch", "risk"]
    description: str
    metric: str
    category: str


class RisksResponse(BaseModel):
    upload_id: str
    risk_count: int
    watch_count: int
    healthy_count: int
    risks: list[RiskItem]


# ──────────────────────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────────────────────
class SummaryResponse(BaseModel):
    upload_id: str
    is_llm: bool = Field(False, description="True when real LLM was used")
    executive_summary: str
    recommendations: list[str]
    key_drivers: list[str]
    confidence_explanation: str
    risk_explanation: str


# ──────────────────────────────────────────────────────────────────────────────
# Report
# ──────────────────────────────────────────────────────────────────────────────
class ReportMetadata(BaseModel):
    upload_id: str
    format: Literal["csv", "pdf"]
    download_url: str


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard (unified)
# ──────────────────────────────────────────────────────────────────────────────
class DashboardResponse(BaseModel):
    upload_id: str
    forecast: ForecastResponse
    channels: list[ChannelAllocation]
    campaigns: list[CampaignForecast]
    optimizer: OptimizerResponse
    risks: list[RiskItem]
    summary: SummaryResponse


# ──────────────────────────────────────────────────────────────────────────────
# Generic
# ──────────────────────────────────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
