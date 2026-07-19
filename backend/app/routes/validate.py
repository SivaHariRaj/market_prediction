"""
POST /validate
Run data-quality checks on an uploaded CSV.
"""
from fastapi import APIRouter, status

from app.models.request_models import ValidateRequest
from app.models.response_models import ValidateResponse
from app.services.validation_service import run_validation

router = APIRouter(prefix="/validate", tags=["Validate"])


@router.post(
    "",
    response_model=ValidateResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate an uploaded CSV",
    description=(
        "Runs 7 data-quality checks: duplicate rows, missing campaigns, "
        "missing values, invalid ROAS, revenue spikes, date formats, negative revenue. "
        "Returns a 0–100 quality score and per-check details."
    ),
)
async def validate_data(body: ValidateRequest) -> ValidateResponse:
    return run_validation(body.upload_id)
