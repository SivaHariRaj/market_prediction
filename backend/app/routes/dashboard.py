"""
GET /dashboard
Unified endpoint that calls forecast, optimizer, risks, and summary internally,
returning a single JSON payload that powers the frontend dashboard.
"""
from fastapi import APIRouter, Query, status

from app.models.response_models import DashboardResponse
from app.services.forecast_service import run_forecast
from app.services.optimizer_service import run_optimizer
from app.services.risk_service import run_risks
from app.services.summary_service import run_summary
from app.utils.exceptions import UploadNotFound
from app.utils.file_utils import find_upload_file
from app.utils.logger import get_logger

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
logger = get_logger(__name__)


@router.get(
    "",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Unified dashboard data",
    description=(
        "Internally calls forecast, optimizer, risks, and summary services. "
        "Returns one unified JSON object that powers the entire frontend dashboard. "
        "Cached per upload_id — call after POST /validate."
    ),
)
async def dashboard(
    upload_id: str = Query(..., description="ID from POST /upload"),
    total_budget: float = Query(default=420_000.0, description="Total monthly budget in USD"),
    horizon_days: int = Query(default=30, ge=1, le=365, description="Forecast horizon in days"),
) -> DashboardResponse:
    if find_upload_file(upload_id) is None:
        raise UploadNotFound(upload_id)

    logger.info("Dashboard request — upload_id=%s budget=%.0f horizon=%d", upload_id, total_budget, horizon_days)

    # ── Run all services ──────────────────────────────────────────────────
    forecast = run_forecast(upload_id, horizon_days=horizon_days)
    optimizer = run_optimizer(upload_id, total_budget=total_budget)
    risks_resp = run_risks(upload_id)
    summary = run_summary(
        upload_id,
        forecast=forecast.model_dump(),
        optimizer=optimizer.model_dump(),
        risks=[r.model_dump() for r in risks_resp.risks],
    )

    return DashboardResponse(
        upload_id=upload_id,
        forecast=forecast,
        channels=optimizer.channels,
        campaigns=forecast.campaign_forecast,
        optimizer=optimizer,
        risks=risks_resp.risks,
        summary=summary,
    )
