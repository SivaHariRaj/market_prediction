"""
POST /optimize
Run rule-based budget optimisation across channels.
"""
from fastapi import APIRouter, status

from app.models.request_models import OptimizerRequest
from app.models.response_models import OptimizerResponse
from app.services.optimizer_service import run_optimizer

router = APIRouter(prefix="/optimize", tags=["Optimizer"])


@router.post(
    "",
    response_model=OptimizerResponse,
    status_code=status.HTTP_200_OK,
    summary="Optimise budget allocation across channels",
    description=(
        "Allocates `total_budget` across advertising channels using ROAS-weighted "
        "proportional splitting, clamped to min/max channel constraints and a ROAS floor. "
        "Returns per-channel budgets, expected revenue, and estimated uplift."
    ),
)
async def optimize(body: OptimizerRequest) -> OptimizerResponse:
    return run_optimizer(
        upload_id=body.upload_id,
        total_budget=body.total_budget,
        min_channel_pct=body.min_channel_pct,
        max_channel_pct=body.max_channel_pct,
        roas_floor=body.roas_floor,
    )
