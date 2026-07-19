"""
POST /summary
Generate an executive summary.
Delegates to summary_service → ml_interface.generate_summary().
"""
from fastapi import APIRouter, status

from app.models.request_models import SummaryRequest
from app.models.response_models import SummaryResponse
from app.services.summary_service import run_summary

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.post(
    "",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate an executive summary",
    description=(
        "Calls `ml_interface.generate_summary()`. If the LLM is not yet implemented, "
        "returns a structured template-based summary with the same response shape. "
        "Accepts optional pre-computed forecast, optimizer, and risk payloads."
    ),
)
async def summary(body: SummaryRequest) -> SummaryResponse:
    return run_summary(
        upload_id=body.upload_id,
        forecast=body.forecast,
        optimizer=body.optimizer,
        risks=body.risks,
    )
