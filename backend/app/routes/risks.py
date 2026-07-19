"""
POST /risks
Detect rule-based risk signals in an uploaded dataset.
"""
from fastapi import APIRouter, status

from app.models.request_models import RisksRequest
from app.models.response_models import RisksResponse
from app.services.risk_service import run_risks

router = APIRouter(prefix="/risks", tags=["Risks"])


@router.post(
    "",
    response_model=RisksResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect risk signals",
    description=(
        "Runs 8 rule-based risk detectors: budget concentration, low ROAS, "
        "revenue instability, campaign saturation, CTR decline, CPA spike, "
        "tracking anomaly, and seasonality. Returns severity: risk | watch | healthy."
    ),
)
async def detect_risks(body: RisksRequest) -> RisksResponse:
    return run_risks(body.upload_id)
