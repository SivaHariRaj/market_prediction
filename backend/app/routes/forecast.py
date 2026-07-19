"""
POST /forecast
Generate a probabilistic revenue & ROAS forecast.
Delegates to forecast_service → ml_interface.predict().
"""
from fastapi import APIRouter, status

from app.models.request_models import ForecastRequest
from app.models.response_models import ForecastResponse
from app.services.forecast_service import run_forecast

router = APIRouter(prefix="/forecast", tags=["Forecast"])


@router.post(
    "",
    response_model=ForecastResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a revenue and ROAS forecast",
    description=(
        "Calls `ml_interface.predict()`. If the ML model is not yet implemented, "
        "returns a deterministic rule-based forecast with the same response shape. "
        "Response includes P10/P50/P90 time series, channel breakdown, and campaign breakdown."
    ),
)
async def forecast(body: ForecastRequest) -> ForecastResponse:
    return run_forecast(body.upload_id, horizon_days=body.horizon_days)
